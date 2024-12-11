"""Tools used to manage the synthesis inputs."""
import json
import logging
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import luigi
import neurots
from luigi.configuration.core import add_config_path
from neurots.validator import ValidationError
from neurots.validator import validate_neuron_distribs
from neurots.validator import validate_neuron_params
from synthesis_workflow.tasks.config import CircuitConfig
from synthesis_workflow.tasks.config import PathConfig
from synthesis_workflow.tasks.config import SynthesisConfig
from synthesis_workflow.tasks.config import reset_default_prefixes
from synthesis_workflow.tasks.synthesis import BuildSynthesisDistributions
from synthesis_workflow.tasks.synthesis import BuildSynthesisParameters

from synthdb.schema import SynthesisInputsTable
from synthdb.schema import commit_and_vacuum
from synthdb.schema import session

TMP_OUT_DIR = Path("out_tmp")
_BASE_PATH = Path(__file__).parent.resolve()
INSITU_SYNTHESIS_INPUTS = _BASE_PATH / "insitu_synthesis_inputs"
SYNTHESIS_INPUTS = _BASE_PATH / "synthesis_inputs"
INPUTS_DIR = SYNTHESIS_INPUTS / "inputs"
LUIGI_CONFIGS_DIR = SYNTHESIS_INPUTS / "luigi_configs"
SYNTHESIS_INPUT_DB = Path(__file__).parent / "synthesis_input_db.yaml"

INPUTS_DIR.mkdir(parents=True, exist_ok=True)
LUIGI_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


def _suffix(brain_region, mtype, luigi_config):
    return f"_{luigi_config}_{brain_region}_{mtype}"


SUBSTITUTION_MAPPINGS = {
    # rename CHC (morph release) into ChC (official name)
    "Isocortex": {
        "L23_ChC": "L23_CHC",
        "L4_ChC": "L4_CHC",
        "L5_ChC": "L5_CHC",
        "L6_ChC": "L6_CHC",
    },
    # create default mtypes (with luigi_Isocortex)
    "default": {
        "GEN_mtype": "L5_TPC:C",
        "GIN_mtype": "L5_SBC",
    },
}


def substitute_mtype(mtype, region, reverse=False, substitutions_mappings=None):
    """Hardcoded substitution rules to match morph release mtype names and expected ones."""
    if substitutions_mappings is None:
        substitutions_mappings = SUBSTITUTION_MAPPINGS

    substitutions_mappings = substitutions_mappings.get(region, {})
    if reverse:
        substitutions_mappings = {val: key for key, val in substitutions_mappings.items()}
    return substitutions_mappings.get(mtype, mtype)


class NotValidError(ValueError):
    """Not valid input parameters."""


class CreateSynthesisInput(luigi.Task):
    """Create synthesis input."""

    mtype = luigi.Parameter()
    luigi_config = luigi.Parameter()
    region = luigi.Parameter(default="base")

    def requires(self):
        """The required tasks."""
        m_type = substitute_mtype(self.mtype, self.region)

        SynthesisConfig().mtypes = [m_type]
        CircuitConfig().region = self.region
        # TODO: add option for scaling rules
        return {
            "distribution": BuildSynthesisDistributions(),
            "parameters": BuildSynthesisParameters(),
        }

    def run(self):
        """Copy the outputs of the required task to the output targets."""
        with open(self.input()["parameters"].path, encoding="utf-8") as param_file:
            params = json.load(param_file)
        params[self.region] = {
            substitute_mtype(mtype, self.region, reverse=True): param
            for mtype, param in params[self.region].items()
        }
        with open(self.output()["params"].path, "w", encoding="utf-8") as param_file:
            json.dump(params, param_file, indent=4, sort_keys=True)

        with open(self.input()["distribution"].path, encoding="utf-8") as distr_file:
            distr = json.load(distr_file)
        distr[self.region] = {
            substitute_mtype(mtype, self.region, reverse=True): distr
            for mtype, distr in distr[self.region].items()
        }
        with open(self.output()["distr"].path, "w", encoding="utf-8") as distr_file:
            json.dump(distr, distr_file, indent=4, sort_keys=True)

        shutil.rmtree(TMP_OUT_DIR)

    def output(self):
        """Define output targets."""
        suffix = _suffix(self.region, self.mtype, self.luigi_config)
        return {
            "params": luigi.LocalTarget(INPUTS_DIR / f"params{suffix}.json"),
            "distr": luigi.LocalTarget(INPUTS_DIR / f"distr{suffix}.json"),
        }


def luigi_config_path(luigi_config):
    """Return the file path of a luigi config."""
    return (LUIGI_CONFIGS_DIR / luigi_config).with_suffix(".cfg")


def input_file_path(file):
    """Format a given input file path to point to the internal input repository."""
    if file is not None:
        file = INPUTS_DIR / file

    return file


def import_file(file):
    """Import the given file into the internal data."""
    file = Path(file)
    imported_file = input_file_path(file.name).absolute()
    if not file.exists() and not imported_file.exists():
        raise ValueError(
            f"The file {file} does not exist either in the current working directory nor in the "
            "internal directory."
        )
    if file.exists() and imported_file.exists():
        raise ValueError(
            f"The file {imported_file} already exists in the internal directory, please change the "
            "name of the imported file."
        )
    if file.exists() and not imported_file.exists():
        shutil.copy(str(file), str(imported_file))
    else:
        logger.debug("The file %s was found in the internal directory.", imported_file)
    return imported_file.name


def check_files_exist(*files, file_type="input"):
    """Check that the given files exist in the repository."""
    missing_files = []
    for file in files:
        if file_type == "luigi_config":
            absolute_file = luigi_config_path(file).absolute()
        else:
            absolute_file = input_file_path(file).absolute()
        logger.debug("Check that the following file exists: %s", absolute_file)
        if not absolute_file.exists():
            missing_files.append(str(absolute_file))

    if missing_files:
        raise ValueError(f"The following files do not exist: {missing_files}")


def check_json_files_not_empty(*files):
    """Check that the given input files are not empty."""
    empty_files = []
    for file in files:
        absolute_file = input_file_path(file).absolute()
        logger.debug("Check that the following file is not empty: %s", absolute_file)
        with open(absolute_file, encoding="utf-8") as f:
            if not json.load(f):
                empty_files.append(str(absolute_file))

    if empty_files:
        raise NotValidError(f"The following files are empty: {empty_files}")


def create_default_input(brain_region, mtype, luigi_config, log_level=None):
    """Create single set of input for an mtype and a luigi.cfg."""
    PathConfig.result_path = TMP_OUT_DIR
    reset_default_prefixes()
    add_config_path(str(luigi_config_path(luigi_config)))

    if log_level is None:  # pragma: no cover
        log_level = logging.WARNING

    if not luigi.build(
        [CreateSynthesisInput(mtype=mtype, region=brain_region, luigi_config=luigi_config)],
        local_scheduler=True,
        log_level=logging.getLevelName(log_level),
    ):  # pragma: no cover
        raise RuntimeError(
            "Could not create default input for "
            f"(brain_region={brain_region}, mtype={mtype}, luigi_config={luigi_config})"
        )

    suffix = _suffix(brain_region, mtype, luigi_config)
    out = {
        "params": f"params{suffix}.json",
        "distrs": f"distr{suffix}.json",
    }

    check_files_exist(out["params"], out["distrs"])
    check_json_files_not_empty(out["params"], out["distrs"])

    return out


def _create_params_distrs(brain_region, mtype, luigi_config, parameters_path, distributions_path):
    """Create parameters and distributions if required."""
    check_files_exist(luigi_config, file_type="luigi_config")

    if parameters_path is None or distributions_path is None:
        created_input = create_default_input(
            brain_region=brain_region, mtype=mtype, luigi_config=luigi_config
        )
    else:
        created_input = {}

    new_params = (
        input_file_path(parameters_path if parameters_path is not None else created_input["params"])
        .relative_to(INPUTS_DIR)
        .as_posix()
    )
    new_distrs = (
        input_file_path(
            distributions_path if distributions_path is not None else created_input["distrs"]
        )
        .relative_to(INPUTS_DIR)
        .as_posix()
    )

    check_files_exist(new_params, new_distrs)

    return new_params, new_distrs


def create_input(brain_region, mtype, luigi_config, parameters_path=None, distributions_path=None):
    """Create input and insert it in the DB for a given set of region, mtype and luigi config."""
    # Check that the given entry does not already exist
    primary_key = (brain_region, mtype, luigi_config)
    selected_input = session.get(SynthesisInputsTable, primary_key)

    if selected_input is not None:
        raise ValueError(f"The following input already exists: {selected_input}")

    if parameters_path is not None:
        parameters_path = import_file(parameters_path)

    if distributions_path is not None:
        distributions_path = import_file(distributions_path)

    # Create new parameters and distributions if they are not provided
    check_files_exist(luigi_config, file_type="luigi_config")
    try:
        new_params, new_distrs = _create_params_distrs(
            brain_region, mtype, luigi_config, parameters_path, distributions_path
        )
    except NotValidError as exc:  # pragma: no cover
        logger.error(exc)
        return

    # Create the new entry in the DB
    new_obj = SynthesisInputsTable(
        brain_region=brain_region,
        mtype=mtype,
        luigi_config=luigi_config,
        distributions_path=new_distrs,
        parameters_path=new_params,
    )

    session.add(new_obj)
    commit_and_vacuum()

    logger.info("New element inserted in the DB: %s", new_obj)


def select_input(brain_region, mtype, luigi_config):
    """Select and return an input entry from the DB."""
    primary_key = (brain_region, mtype, luigi_config)
    selected_input = session.get(SynthesisInputsTable, primary_key)

    if selected_input is None:
        raise ValueError(f"Could not retrieve inputs for {primary_key}")

    return selected_input


def get_entries_from_values(luigi_config=None, parameters_path=None, distributions_path=None):
    """Select and return the input entries from the DB that share a given common value."""
    query = session.query(SynthesisInputsTable)
    if luigi_config is not None:
        query = query.filter(SynthesisInputsTable.luigi_config == luigi_config)
    if parameters_path is not None:
        query = query.filter(SynthesisInputsTable.parameters_path == parameters_path)
    if distributions_path is not None:
        query = query.filter(SynthesisInputsTable.distributions_path == distributions_path)
    return query.all()


def remove_orphans(luigi_config=None, parameters_path=None, distributions_path=None):
    """Remove luigi config, parameter and distribution files that are not used by input entries."""
    # Remove the luigi config file if it is not used by any input entry
    if luigi_config and not get_entries_from_values(luigi_config=luigi_config):
        luigi_config = luigi_config_path(luigi_config)
        os.remove(luigi_config)
        logger.info("Removed file for not being used by any input entry: %s", luigi_config)

    # Remove the parameters file if it is not used by any input entry
    if parameters_path and not get_entries_from_values(parameters_path=parameters_path):
        parameters_path = input_file_path(parameters_path)
        os.remove(parameters_path)
        logger.info("Removed file for not being used by any input entry: %s", parameters_path)

    # Remove the distributions file if it is not used by any input entry
    if distributions_path and not get_entries_from_values(distributions_path=distributions_path):
        distributions_path = input_file_path(distributions_path)
        os.remove(distributions_path)
        logger.info("Removed file for not being used by any input entry: %s", distributions_path)


def update_input(brain_region, mtype, luigi_config, parameters_path=None, distributions_path=None):
    """Update path of an input in the DB for a given set of region, mtype and luigi config."""
    selected_input = select_input(brain_region, mtype, luigi_config)

    if parameters_path == "auto" or distributions_path == "auto":
        try:
            new_params, new_distrs = _create_params_distrs(
                brain_region, mtype, luigi_config, None, None
            )
        except NotValidError as exc:  # pragma: no cover
            logger.error(exc)
            return

        if parameters_path == "auto":
            parameters_path = new_params
        if distributions_path == "auto":
            distributions_path = new_distrs

    if parameters_path is not None:
        selected_input.parameters_path = import_file(parameters_path)
    if distributions_path is not None:
        selected_input.distributions_path = import_file(distributions_path)

    # Check that the input files exist before updating the entry in the DB
    check_files_exist(selected_input.parameters_path, selected_input.distributions_path)
    check_files_exist(selected_input.luigi_config, file_type="luigi_config")

    commit_and_vacuum()

    logger.info("Element updated in the DB: %s", selected_input)

    # Remove the files that are not used by any input entry
    remove_orphans(
        selected_input.luigi_config,
        selected_input.parameters_path,
        selected_input.distributions_path,
    )


def remove_input(brain_region, mtype, luigi_config):
    """Remove the given input from the DB."""
    inputs = list_inputs(brain_region=brain_region, mtype=mtype, luigi_config=luigi_config)
    for selected_input in inputs:
        # Remove the entry from the DB
        session.delete(selected_input)
        commit_and_vacuum()

        logger.info("Element removed from the DB: %s", selected_input)

        # Remove the files that are not used by any input entry
        try:
            remove_orphans(
                luigi_config, selected_input.parameters_path, selected_input.distributions_path
            )
        except FileNotFoundError:  # pragma: no cover
            pass


def rebuild_input(brain_region, mtype, luigi_config):
    """Rebuild the parameters and distributions for a given input."""
    selected_input = select_input(brain_region, mtype, luigi_config)
    query = session.query(SynthesisInputsTable)
    distrs_query = query.filter(
        SynthesisInputsTable.distributions_path == selected_input.distributions_path
    )
    params_query = query.filter(
        SynthesisInputsTable.parameters_path == selected_input.parameters_path
    )

    def _check_entries(check_query, file_name):
        entries = check_query.all()

        if len(entries) > 1:
            log_func = logger.warning
        else:
            log_func = logger.info

        log_func(
            "Rebuilding the file '%s' used by the following entries:\n\t%s",
            file_name,
            "\n\t".join(sorted(str(i) for i in entries)),
        )
        return input_file_path(file_name)

    distrs_file = _check_entries(distrs_query, selected_input.distributions_path)
    params_file = _check_entries(params_query, selected_input.parameters_path)

    logger.debug("Removing the file '%s'", distrs_file.name)
    distrs_file.unlink()

    logger.debug("Removing the file '%s'", params_file.name)
    params_file.unlink()

    update_input(
        brain_region, mtype, luigi_config, parameters_path="auto", distributions_path="auto"
    )


def list_inputs(brain_region=None, mtype=None, luigi_config=None):
    """List inputs in the DB with given filters for a given set of region, mtype or luigi config."""
    query = session.query(SynthesisInputsTable)
    if brain_region is not None:
        query = query.filter(SynthesisInputsTable.brain_region == brain_region)
    if mtype is not None:
        query = query.filter(SynthesisInputsTable.mtype == mtype)
    if luigi_config is not None:
        query = query.filter(SynthesisInputsTable.luigi_config == luigi_config)

    return query.all()


def load_internal_file(internal_path):
    """Load an internal JSON file from its name."""
    with open(str(INPUTS_DIR / internal_path), encoding="utf-8") as f:
        data = json.load(f)
    data = neurots.utils.convert_from_legacy_neurite_type(data)
    return data


def pull_inputs(
    brain_region=None,
    mtype=None,
    luigi_config=None,
    output_path=None,
    concatenate=False,
    inner_only=False,
):
    """Pull input json and append new data if file already present."""
    # pylint: disable=too-many-locals
    if inner_only and concatenate:
        raise ValueError("Cannot use inner-only and concatenate together")

    logger.info(
        "Pulling inputs for brain_region=%s ; mtype=%s ; luigi_config=%s",
        brain_region,
        mtype,
        luigi_config,
    )
    inputs = list_inputs(brain_region=brain_region, mtype=mtype, luigi_config=luigi_config)

    if not inputs:
        raise ValueError(
            f"Could not retrieve any input for brain_region={brain_region} ; mtype={mtype} ; "
            f"luigi_config={luigi_config}"
        )

    output_path = Path(output_path or ".")
    output_path.mkdir(parents=True, exist_ok=True)

    outputs = []
    if concatenate:
        distr = {}
        params = {}
    for selected_input in inputs:
        if concatenate:
            suffix = ""
        else:
            suffix = _suffix(
                selected_input.brain_region, selected_input.mtype, selected_input.luigi_config
            )
        params_to = output_path / f"tmd_parameters{suffix}.json"
        distr_to = output_path / f"tmd_distributions{suffix}.json"

        outputs.append(
            {
                "brain_region": selected_input.brain_region,
                "mtype": selected_input.mtype,
                "luigi_config": selected_input.luigi_config,
                "parameters_path": selected_input.parameters_path,
                "distributions_path": selected_input.distributions_path,
                "output_parameters_path": params_to,
                "output_distributions_path": distr_to,
            }
        )

        if (
            concatenate
            and selected_input.brain_region
            not in distr  # pylint: disable=possibly-used-before-assignment
        ):
            distr[selected_input.brain_region] = {}
        elif not concatenate:
            distr = {selected_input.brain_region: {}}

        if (
            concatenate
            and selected_input.brain_region
            not in params  # pylint: disable=possibly-used-before-assignment
        ):
            params[selected_input.brain_region] = {}
        elif not concatenate:
            params = {selected_input.brain_region: {}}

        input_params = INPUTS_DIR / selected_input.parameters_path
        input_distrs = INPUTS_DIR / selected_input.distributions_path
        check_files_exist(input_params, input_distrs)

        logger.info("Reading distributions from %s", input_distrs)
        _distr = load_internal_file(input_distrs)
        distr[selected_input.brain_region].update(_distr[selected_input.brain_region])

        logger.info("Reading parameters from %s", input_params)
        _param = load_internal_file(input_params)
        params[selected_input.brain_region].update(_param[selected_input.brain_region])

        logger.info("Exporting distributions to %s", distr_to)
        if inner_only:
            distr = distr[selected_input.brain_region][selected_input.mtype]
            params = params[selected_input.brain_region][selected_input.mtype]

        if not concatenate:
            with open(distr_to, "w", encoding="utf-8") as f:
                json.dump(distr, f, indent=4, sort_keys=True)

            logger.info("Exporting parameters to %s", params_to)
            with open(params_to, "w", encoding="utf-8") as f:
                json.dump(params, f, indent=4, sort_keys=True)

    if concatenate:
        with open(distr_to, "w", encoding="utf-8") as f:
            json.dump(distr, f, indent=4, sort_keys=True)

        logger.info("Exporting parameters to %s", params_to)
        with open(params_to, "w", encoding="utf-8") as f:
            json.dump(params, f, indent=4, sort_keys=True)

    return outputs


def validate_inputs():
    """Check that all inputs are valid after being pulled."""
    with TemporaryDirectory() as tmpdir:
        pulled = pull_inputs(output_path=tmpdir)

        all_messages = []
        logger.info("Pulled all inputs to %s", tmpdir)

        for i in pulled:
            params_path = i["output_parameters_path"]
            logger.debug("Validate parameters from %s", params_path)
            params = load_internal_file(params_path)
            for region, params_region in params.items():
                for mtype, params_mtype in params_region.items():
                    try:
                        validate_neuron_params(params_mtype)
                    except ValidationError as exc:
                        all_messages.append(
                            f"The file {params_path} is not valid for the mtype {mtype} and region "
                            f"{region} for the following reason:\n{exc}"
                        )

            distrs_path = i["output_distributions_path"]
            logger.debug("Validate distributions from %s", distrs_path)
            distrs = load_internal_file(distrs_path)
            for region, distrs_region in distrs.items():
                for mtype, distrs_mtype in distrs_region.items():
                    try:
                        validate_neuron_distribs(distrs_mtype)
                    except ValidationError as exc:
                        all_messages.append(
                            f"The file {distrs_path} is not valid for the mtype {mtype} and region "
                            f"{region} for the following reason:\n{exc}"
                        )

        if all_messages:
            raise ValidationError("\n\n".join(all_messages))

        logger.info("All internal inputs are valid for 'NeuroTS==%s'", neurots.__version__)
