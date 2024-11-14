"""Command Line Interface for the synthdb package.

synthdb pull <mtype> <species> <brain_region> <luigi_config> --to <output_path>
"""

import configparser
import logging

import click
from synthesis_workflow.tools import load_neurondb_to_dataframe

from synthdb.input_tools import create_input
from synthdb.input_tools import list_inputs
from synthdb.input_tools import luigi_config_path
from synthdb.input_tools import pull_inputs
from synthdb.input_tools import rebuild_input
from synthdb.input_tools import remove_input
from synthdb.input_tools import update_input
from synthdb.input_tools import validate_inputs
from synthdb.morph_release_tools import create_release
from synthdb.morph_release_tools import list_releases
from synthdb.morph_release_tools import remove_release
from synthdb.morph_release_tools import update_release
from synthdb.schema import SynthesisInputsTable
from synthdb.schema import engine
from synthdb.schema import session

logger = logging.getLogger(__name__)

_SPECIES = {
    "type": str,
    "help": "The name of the species as stored in the DB.",
}
_BRAIN_REGION = {
    "type": str,
    "help": "The name of the brain region as stored in the DB.",
}
_MTYPE = {
    "type": str,
    "help": "The name of the mtype as stored in the DB.",
}
_LUIGI_CONFIG_SYNTH_INPUTS = {
    "type": str,
    "help": (
        "The name of the luigi configuration as stored in the DB. The actual file must "
        "be located in the `synthdb/synthesis_inputs/luigi_configs` directory."
    ),
}
_LUIGI_CONFIG_MORPH_RELEASES = {
    "type": str,
    "help": (
        "The name of the luigi configuration as stored in the DB. The actual file must "
        "be located in the `synthdb/morphology_releases/luigi_configs` directory."
    ),
}
_PARAMS_PATH = {
    "type": str,
    "help": "Internal path to the parameters that should be mapped to this entry.",
}
_DISTRS_PATH = {
    "type": str,
    "help": "Internal path to the distributions that should be mapped to this entry.",
}
_GPFS_PATH = {
    "type": str,
    "help": "Path to the morphology release on GPFS.",
}
_PIP_LIST = {
    "type": str,
    "help": (
        "The result of the `pip list --format json` command in the environment used to generate the"
        " morphology release."
    ),
}


def _setup_logger(verbose):
    level = (logging.WARNING, logging.INFO, logging.DEBUG)[min(verbose, 2)]
    logging.basicConfig(level=level)

    logging.getLogger("luigi").level = level
    logging.getLogger("luigi-interface").level = level
    logging.getLogger("luigi_tools.task").disabled = True

    if level == logging.DEBUG:
        # Log SQL queries
        engine.echo = True

        # Deduplicate engine loggers
        logging.getLogger("sqlalchemy").propagate = False


@click.group()
@click.version_option()
@click.option(
    "-v", "--verbose", count=True, default=0, help="Default is WARNING, -v for INFO, -vv for DEBUG"
)
def cli(verbose):
    """The CLI entry point of SynthDB."""
    _setup_logger(verbose)


@cli.group()
def synthesis_inputs():
    """The CLI entry point of the synthesis-inputs sub-command of SynthDB."""
    return


@synthesis_inputs.command("create")
@click.argument("species")
@click.argument("brain_region")
@click.argument("luigi_config")
@click.option("--mtype", **_MTYPE)
@click.option("--parameters-path", **_PARAMS_PATH)
@click.option("--distributions-path", **_DISTRS_PATH)
def create(species, brain_region, luigi_config, mtype, parameters_path, distributions_path):
    """Create a new entry in the database.

    SPECIES is the name of the species as stored in the DB.

    BRAIN_REGION is the name of the brain region as stored in the DB.

    LUIGI_CONFIG is the name of the luigi configuration as stored in the DB. The actual file must
    be located in the `synthdb/synthesis_inputs/luigi_configs` directory.

    If the parameters and/or distributions paths are not provided, the parameters and/or
    distributions will be computed from the biological cells using the ``synthesis-workflow``
    package.
    """
    if mtype is None:  # pragma: no cover
        logger.warning("We guess mtypes from input dataset, substitution rules are not applied")
        config = configparser.ConfigParser()
        with open(luigi_config_path(luigi_config).absolute(), encoding="utf-8") as f:
            config.read_file(f)
        neurondb_path = config.get("BuildMorphsDF", "neurondb_path")

        morphs_df = load_neurondb_to_dataframe(neurondb_path)
        mtypes = morphs_df.mtype.unique()
        for i, _mtype in enumerate(mtypes):
            primary_key = (species, brain_region, _mtype, luigi_config)
            print(f"Building {i + 1} / {len(mtypes)}: {primary_key}")
            selected_input = session.get(SynthesisInputsTable, primary_key)

            if selected_input is None:  # pragma: no cover
                logger.info("Creating mtype: %s", _mtype)
                create_input(
                    species,
                    brain_region,
                    _mtype,
                    luigi_config,
                    parameters_path=parameters_path,
                    distributions_path=distributions_path,
                )
    else:
        create_input(
            species, brain_region, mtype, luigi_config, parameters_path, distributions_path
        )


@synthesis_inputs.command("update")
@click.argument("species")
@click.argument("brain_region")
@click.argument("mtype")
@click.argument("luigi_config")
@click.option("--parameters-path", **_PARAMS_PATH)
@click.option("--distributions-path", **_DISTRS_PATH)
def update(species, brain_region, mtype, luigi_config, parameters_path, distributions_path):
    """Update an entry in the database.

    SPECIES is the name of the species as stored in the DB.

    BRAIN_REGION is the name of the brain region as stored in the DB.

    MTYPE is the name of the mtype as stored in the DB.

    LUIGI_CONFIG is the name of the luigi configuration as stored in the DB. The actual file must
    be located in the `synthdb/synthesis_inputs/luigi_configs` directory.

    If the parameters and/or distributions paths are not provided, the parameters and/or
    distributions will be computed from the biological cells using the ``synthesis-workflow``
    package.
    """
    update_input(species, brain_region, mtype, luigi_config, parameters_path, distributions_path)


@synthesis_inputs.command("rebuild")
@click.option("--species", **_SPECIES)
@click.option("--brain-region", **_BRAIN_REGION)
@click.option("--mtype", **_MTYPE)
@click.option("--luigi-config", **_LUIGI_CONFIG_SYNTH_INPUTS)
def rebuild(luigi_config, species, brain_region, mtype):
    """Rebuild entries in the database according to the given filters with default values."""
    listed_elements = list_inputs(species, brain_region, mtype, luigi_config)
    for i, element in enumerate(listed_elements):
        print(f"Rebuilding {i + 1} / {len(listed_elements)}: {element}")
        rebuild_input(element.species, element.brain_region, element.mtype, element.luigi_config)


@synthesis_inputs.command("remove")
@click.option("--species", **_SPECIES)
@click.option("--brain-region", **_BRAIN_REGION)
@click.option("--mtype", **_MTYPE)
@click.option("--luigi-config", **_LUIGI_CONFIG_SYNTH_INPUTS)
def remove(species, brain_region, mtype, luigi_config):
    """Remove entries in the database."""
    remove_input(species, brain_region, mtype, luigi_config)


@synthesis_inputs.command("list")
@click.option("--species", **_SPECIES)
@click.option("--brain-region", **_BRAIN_REGION)
@click.option("--mtype", **_MTYPE)
@click.option("--luigi-config", **_LUIGI_CONFIG_SYNTH_INPUTS)
def list_entries(species, brain_region, mtype, luigi_config):
    """List entries in the database.

    If several filters are given, the listed entries will satisfy all of them.
    """
    listed_elements = list_inputs(species, brain_region, mtype, luigi_config)
    print(f"Found {len(listed_elements)} entries")
    for i in listed_elements:
        print(i)


@synthesis_inputs.command("pull")
@click.option("--brain-region", **_BRAIN_REGION)
@click.option("--mtype", **_MTYPE)
@click.option("--luigi-config", **_LUIGI_CONFIG_SYNTH_INPUTS)
@click.option(
    "--output-path", type=str, help="The directory in which the inputs will be extracted."
)
@click.option(
    "--concatenate",
    is_flag=True,
    show_default=True,
    default=False,
    help="concatenate all possible datasets into one file",
)
@click.option(
    "--inner-only",
    is_flag=True,
    show_default=True,
    default=False,
    help="Save only the data, not the region/mtpe keys (works for a single dataset query)",
)
def pull(brain_region, mtype, luigi_config, output_path, concatenate, inner_only):
    """Pull entries from the database to generate inputs.

    List all entries according to the filters provided and generate the input files for each entry.

    If several filters are given, the extracted entries will satisfy all of them.
    """
    pull_inputs(
        brain_region,
        mtype,
        luigi_config,
        output_path=output_path,
        concatenate=concatenate,
        inner_only=inner_only,
    )


@synthesis_inputs.command("validate")
def validate():
    """Validate all inputs after they are pulled from the database."""
    validate_inputs()


@cli.group()
def morphology_release():
    """The CLI entry point of the morphology-release sub-command of SynthDB."""
    return


@morphology_release.command("create")
@click.argument("name")
@click.option("--gpfs-path", required=True, **_GPFS_PATH)
@click.option("--pip-list", **_PIP_LIST)
@click.option("--luigi-config", **_LUIGI_CONFIG_MORPH_RELEASES)
def create_morphology_release(name, gpfs_path, pip_list, luigi_config):
    """Create a new entry in the database.

    NAME is the name of the morphology release as stored in the DB.

    If the pip_list JSON string is not provided, it will be automatically generated using the
    `pip list --format json` command.
    """
    create_release(name, gpfs_path, pip_list, luigi_config)


@morphology_release.command("update")
@click.argument("name")
@click.option("--gpfs-path", **_GPFS_PATH)
@click.option("--pip-list", **_PIP_LIST)
@click.option("--luigi-config", **_LUIGI_CONFIG_MORPH_RELEASES)
def update_morphology_release(name, gpfs_path, pip_list, luigi_config):
    """Update an entry in the database.

    NAME is the name of the morphology release as stored in the DB.

    If the pip_list JSON string is not provided, it will be automatically generated using the
    `pip list --format json` command.
    """
    update_release(name, gpfs_path, pip_list, luigi_config)


@morphology_release.command("remove")
@click.argument("name")
def remove_morphology_release(name):
    """Remove an entry in the database.

    NAME is the name of the morphology release as stored in the DB.
    """
    remove_release(name)


@morphology_release.command("list")
@click.option(
    "--with-pip-list",
    help="Print the pip list entries for each morphology release.",
    is_flag=True,
    show_default=True,
    default=False,
)
def list_morphology_releases(with_pip_list):
    """List morphology release entries in the database."""
    listed_elements = list_releases()
    for i in listed_elements:
        msg = f"{i.name}: gpfs_path={i.gpfs_path} ; luigi_config={i.luigi_config}"
        if with_pip_list:
            msg += f" ; pip_list={i.pip_list}"
        print(msg)
