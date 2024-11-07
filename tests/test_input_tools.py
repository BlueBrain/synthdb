"""Test functions from synthdb.input_tools."""

# pylint: disable=unused-argument
# pylint: disable=use-implicit-booleaness-not-comparison
import json
import logging
import re
import shutil
from pathlib import Path

import pytest

import synthdb.input_tools
import synthdb.schema


@pytest.mark.parametrize(
    "mtype,region,mapping",
    [
        pytest.param("GEN_mtype", "default", None, id="Default mapping"),
        pytest.param(
            "GEN_mtype", "default", synthdb.input_tools.SUBSTITUTION_MAPPINGS, id="Specific mapping"
        ),
        pytest.param("UNKNOWN", "default", None, id="Unknown mtype"),
        pytest.param("GEN_mtype", "UNKNOWN", None, id="Unknown region"),
    ],
)
def test_substitute_mtype(mtype, region, mapping):
    """Test the mtype mapping."""
    mapped_mtype = synthdb.input_tools.substitute_mtype(
        mtype, region, substitutions_mappings=mapping
    )
    if mtype == "UNKNOWN":
        assert mapped_mtype == "UNKNOWN"
    elif region == "UNKNOWN":
        assert mapped_mtype == "GEN_mtype"
    else:
        assert mapped_mtype == "L5_TPC:C"


@pytest.mark.parametrize(
    "mtype,region,mapping",
    [
        pytest.param("L5_TPC:C", "default", None, id="Default mapping"),
        pytest.param(
            "L5_TPC:C", "default", synthdb.input_tools.SUBSTITUTION_MAPPINGS, id="Specific mapping"
        ),
        pytest.param("UNKNOWN", "default", None, id="Unknown mtype"),
        pytest.param("L5_TPC:C", "UNKNOWN", None, id="Unknown region"),
    ],
)
def test_substitute_mtype_reverse(mtype, region, mapping):
    """Test the reverse mtype mapping."""
    mapped_mtype = synthdb.input_tools.substitute_mtype(
        mtype, region, reverse=True, substitutions_mappings=mapping
    )
    if mtype == "UNKNOWN":
        assert mapped_mtype == "UNKNOWN"
    elif region == "UNKNOWN":
        assert mapped_mtype == "L5_TPC:C"
    else:
        assert mapped_mtype == "GEN_mtype"


@pytest.mark.parametrize(
    "file_name",
    [
        pytest.param(None, id="None file name"),
        pytest.param("test.file", id="Not None file name"),
    ],
)
def test_input_file_path(file_name):
    """Test that input file path are properly generated."""
    if file_name is None:
        assert synthdb.input_tools.input_file_path(file_name) is None
    else:
        assert (
            synthdb.input_tools.input_file_path(file_name)
            == synthdb.input_tools.INPUTS_DIR / file_name
        )


def test_check_files_exist():
    """Test that existing files are checked properly."""
    synthdb.input_tools.check_files_exist("params_luigi_Isocortex_Isocortex_L4_UPC.json")
    synthdb.input_tools.check_files_exist("luigi_Isocortex", file_type="luigi_config")

    msg = (
        "The following files do not exist: "
        f"\\['{str(synthdb.input_tools.INPUTS_DIR / 'not_existing_file')}'\\]"
    )
    with pytest.raises(ValueError, match=msg):
        synthdb.input_tools.check_files_exist("not_existing_file")

    msg = (
        "The following files do not exist: "
        f"\\['{str(synthdb.input_tools.LUIGI_CONFIGS_DIR / 'not_existing_file.cfg')}'\\]"
    )
    with pytest.raises(ValueError, match=msg):
        synthdb.input_tools.check_files_exist("not_existing_file", file_type="luigi_config")


def test_check_json_files_not_empty(tmpdir):
    """Test that not empty files are checked properly."""
    not_empty_file_path = tmpdir / "not_empty.json"
    with open(not_empty_file_path, mode="w", encoding="utf-8") as f:
        json.dump({"not_empty": "a value"}, f)

    empty_file_path = tmpdir / "empty.json"
    with open(empty_file_path, mode="w", encoding="utf-8") as f:
        json.dump({}, f)

    synthdb.input_tools.check_json_files_not_empty(not_empty_file_path)

    msg = f"The following files are empty: \\['{str(empty_file_path)}'\\]"
    with pytest.raises(synthdb.input_tools.NotValidError, match=msg):
        synthdb.input_tools.check_json_files_not_empty(empty_file_path)


def test_select_input(internal_db_session, saved_db_session):
    """Test element selection."""
    base_element = synthdb.input_tools.select_input("Isocortex", "L4_UPC", "luigi_Isocortex")
    assert base_element.brain_region == "Isocortex"
    assert base_element.mtype == "L4_UPC"
    assert base_element.luigi_config == "luigi_Isocortex"

    unknown_key = ("UNKNOWN", "UNKNOWN", "UNKNOWN")
    msg = re.escape(f"Could not retrieve inputs for {unknown_key}")
    with pytest.raises(ValueError, match=msg):
        synthdb.input_tools.select_input(*unknown_key)


def test_create_with_params_and_distrs(internal_db_session, saved_db_session):
    """Test element creation with given params and distrs."""
    base_element = saved_db_session.get(
        synthdb.schema.SynthesisInputsTable, ("Isocortex", "L4_UPC", "luigi_Isocortex")
    )

    primary_key = ("test_region", "test_mtype", "luigi_Isocortex")
    synthdb.input_tools.create_input(
        *primary_key,
        parameters_path=base_element.parameters_path,
        distributions_path=base_element.distributions_path,
    )

    created_element = internal_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)
    assert created_element.parameters_path == base_element.parameters_path
    assert created_element.distributions_path == base_element.distributions_path


def test_create_automatic(internal_db_session, saved_db_session, mock_synthesis):
    """Test element creation with no given params and distrs."""
    primary_key = ("Isocortex", "L4_UPC", "luigi_Isocortex")
    base_internal_element = internal_db_session.get(
        synthdb.schema.SynthesisInputsTable, primary_key
    )
    internal_db_session.delete(base_internal_element)
    internal_db_session.commit()
    synthdb.input_tools.input_file_path(base_internal_element.parameters_path).unlink()
    synthdb.input_tools.input_file_path(base_internal_element.distributions_path).unlink()

    synthdb.input_tools.create_input(*primary_key)

    base_element = saved_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)
    created_element = internal_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)
    assert created_element.parameters_path == base_element.parameters_path
    assert created_element.distributions_path == base_element.distributions_path


def test_create_existing(internal_db_session, saved_db_session):
    """Test element creation with no given params and distrs."""
    primary_key = ("Isocortex", "L4_UPC", "luigi_Isocortex")
    base_internal_element = internal_db_session.get(
        synthdb.schema.SynthesisInputsTable, primary_key
    )

    with pytest.raises(
        ValueError, match=re.escape(f"The following input already exists: {base_internal_element}")
    ):
        synthdb.input_tools.create_input(*primary_key)


def test_create_imported_file(internal_db_session, saved_db_session, tmpdir, caplog):
    """Test element creation with imported params and distrs."""
    primary_key = ("Isocortex", "L4_UPC", "luigi_Isocortex")
    base_internal_element = internal_db_session.get(
        synthdb.schema.SynthesisInputsTable, primary_key
    )
    internal_db_session.delete(base_internal_element)
    internal_db_session.commit()

    # Copy files to tmpdir to test import feature
    input_parameters_path = synthdb.input_tools.input_file_path(
        base_internal_element.parameters_path
    )
    parameters_path = tmpdir / base_internal_element.parameters_path
    shutil.copy(
        input_parameters_path,
        parameters_path,
    )
    input_parameters_path.unlink()

    input_distributions_path = synthdb.input_tools.input_file_path(
        base_internal_element.distributions_path
    )
    distributions_path = tmpdir / base_internal_element.distributions_path
    shutil.copy(
        input_distributions_path,
        distributions_path,
    )
    input_distributions_path.unlink()

    new_primary_key = ("test_region", "test_mtype", "luigi_Isocortex")

    synthdb.input_tools.create_input(
        *new_primary_key,
        parameters_path=parameters_path,
        distributions_path=distributions_path,
    )

    base_element = saved_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)
    created_element = internal_db_session.get(synthdb.schema.SynthesisInputsTable, new_primary_key)
    assert created_element.parameters_path == base_element.parameters_path
    assert created_element.distributions_path == base_element.distributions_path

    # Test that importing the same files again fails because they now already exist in the internal
    # directory.
    with pytest.raises(
        ValueError,
        match=(
            f"The file {input_parameters_path} already exists in the internal directory, please "
            "change the name of the imported file."
        ),
    ):
        synthdb.input_tools.create_input(
            "test_region_2",
            "test_mtype_2",
            "luigi_Isocortex",
            parameters_path=parameters_path,
            distributions_path=None,
        )
    with pytest.raises(
        ValueError,
        match=(
            f"The file {input_distributions_path} already exists in the internal directory, please "
            "change the name of the imported file."
        ),
    ):
        synthdb.input_tools.create_input(
            "test_region_2",
            "test_mtype_2",
            "luigi_Isocortex",
            parameters_path=None,
            distributions_path=distributions_path,
        )

    # Test that importing an file that does not exist fails.
    with pytest.raises(
        ValueError,
        match=(
            "The file UNKNOWN PARAMS does not exist either in the current working directory nor in "
            "the internal directory."
        ),
    ):
        synthdb.input_tools.create_input(
            "test_region_2",
            "test_mtype_2",
            "luigi_Isocortex",
            parameters_path="UNKNOWN PARAMS",
            distributions_path="UNKNOWN DISTRS",
        )

    # Test that a logger entry is properly emitted when the file only exists in the internal
    # directory.
    caplog.clear()
    caplog.set_level(logging.DEBUG)
    synthdb.input_tools.create_input(
        "test_region_2",
        "test_mtype_2",
        "luigi_Isocortex",
        parameters_path=created_element.parameters_path,
        distributions_path=created_element.distributions_path,
    )
    assert [
        i[2]
        for i in caplog.record_tuples
        if i[0] == "synthdb.input_tools" and i[1] == logging.DEBUG
    ][:2] == [
        f"The file {input_parameters_path} was found in the internal directory.",
        f"The file {input_distributions_path} was found in the internal directory.",
    ]


def test_update(internal_db_session, saved_db_session, tmpdir, caplog):
    """Test element update."""
    primary_key = ("Isocortex", "L4_UPC", "luigi_Isocortex")
    base_internal_element = internal_db_session.get(
        synthdb.schema.SynthesisInputsTable, primary_key
    )

    other_primary_key = ("Isocortex", "L5_UPC", "luigi_Isocortex")
    other_element = saved_db_session.get(synthdb.schema.SynthesisInputsTable, other_primary_key)

    # Manually update values
    synthdb.input_tools.update_input(
        *primary_key,
        parameters_path=other_element.parameters_path,
        distributions_path=other_element.distributions_path,
    )

    # Check updated element
    updated_element = internal_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)
    assert updated_element.parameters_path == other_element.parameters_path
    assert updated_element.distributions_path == other_element.distributions_path

    # Update the parameter value automatically (should reset to initial value)
    synthdb.input_tools.update_input(
        *primary_key, parameters_path="auto", distributions_path=other_element.distributions_path
    )

    # Check updated element
    updated_element = internal_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)
    assert updated_element.parameters_path == base_internal_element.parameters_path
    assert updated_element.distributions_path == other_element.distributions_path

    # Update the distribution value automatically (should reset to initial value)
    synthdb.input_tools.update_input(
        *primary_key, parameters_path=other_element.parameters_path, distributions_path="auto"
    )

    # Check updated element
    updated_element = internal_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)
    assert updated_element.parameters_path == other_element.parameters_path
    assert updated_element.distributions_path == base_internal_element.distributions_path

    # Update the values automatically (should reset to initial values)
    synthdb.input_tools.update_input(
        *primary_key, parameters_path="auto", distributions_path="auto"
    )

    # Check updated element
    updated_element = internal_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)
    assert updated_element.parameters_path == base_internal_element.parameters_path
    assert updated_element.distributions_path == base_internal_element.distributions_path

    # Update only the parameter values
    synthdb.input_tools.update_input(*primary_key, parameters_path=other_element.parameters_path)

    # Check updated element
    updated_element = internal_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)
    assert updated_element.parameters_path == other_element.parameters_path
    assert updated_element.distributions_path == base_internal_element.distributions_path

    # Update only the distribution values
    synthdb.input_tools.update_input(
        *primary_key, distributions_path=other_element.distributions_path
    )

    # Check updated element
    updated_element = internal_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)
    assert updated_element.parameters_path == other_element.parameters_path
    assert updated_element.distributions_path == other_element.distributions_path

    # Copy files to tmpdir to test import feature
    input_parameters_path = synthdb.input_tools.input_file_path(
        base_internal_element.parameters_path
    )
    parameters_path = tmpdir / base_internal_element.parameters_path
    shutil.copy(
        input_parameters_path,
        parameters_path,
    )

    input_distributions_path = synthdb.input_tools.input_file_path(
        base_internal_element.distributions_path
    )
    distributions_path = tmpdir / base_internal_element.distributions_path
    shutil.copy(
        input_distributions_path,
        distributions_path,
    )

    # Test that importing the same files again fails because they now already exist in the internal
    # directory.
    with pytest.raises(
        ValueError,
        match=(
            f"The file {input_parameters_path} already exists in the internal directory, please "
            "change the name of the imported file."
        ),
    ):
        synthdb.input_tools.update_input(
            *primary_key,
            parameters_path=parameters_path,
            distributions_path=None,
        )
    with pytest.raises(
        ValueError,
        match=(
            f"The file {input_distributions_path} already exists in the internal directory, please "
            "change the name of the imported file."
        ),
    ):
        synthdb.input_tools.update_input(
            *primary_key,
            parameters_path=None,
            distributions_path=distributions_path,
        )

    # Test that importing an file that does not exist fails.
    with pytest.raises(
        ValueError,
        match=(
            "The file UNKNOWN PARAMS does not exist either in the current working directory nor in "
            "the internal directory."
        ),
    ):
        synthdb.input_tools.update_input(
            *primary_key,
            parameters_path="UNKNOWN PARAMS",
            distributions_path="UNKNOWN DISTRS",
        )

    # Test that a logger entry is properly emitted when the file only exists in the internal
    # directory.
    caplog.clear()
    caplog.set_level(logging.DEBUG)
    synthdb.input_tools.update_input(
        *primary_key,
        parameters_path=updated_element.parameters_path,
        distributions_path=updated_element.distributions_path,
    )
    assert [
        i[2]
        for i in caplog.record_tuples
        if i[0] == "synthdb.input_tools" and i[1] == logging.DEBUG
    ][:2] == [
        f"The file {input_parameters_path} was found in the internal directory.",
        f"The file {input_distributions_path} was found in the internal directory.",
    ]


def test_rebuild(internal_db_session, saved_db_session, mock_synthesis, caplog):
    """Test element rebuild."""
    primary_key = ("Isocortex", "L5_UPC", "luigi_Isocortex")
    base_internal_element = internal_db_session.get(
        synthdb.schema.SynthesisInputsTable, primary_key
    )

    # Remove the content of parameters and distributions files
    with synthdb.input_tools.input_file_path(base_internal_element.parameters_path).open(
        "w", encoding="utf-8"
    ) as f:
        json.dump({}, f)
    with synthdb.input_tools.input_file_path(base_internal_element.distributions_path).open(
        "w", encoding="utf-8"
    ) as f:
        json.dump({}, f)

    caplog.clear()
    caplog.set_level(logging.DEBUG)

    # Rebuild files
    synthdb.input_tools.rebuild_input(*primary_key)

    messages = [i for i in caplog.record_tuples if i[0] == "synthdb.input_tools"]

    assert [i[2] for i in messages[:4]] == [
        (
            "Rebuilding the file 'distr_luigi_Isocortex_Isocortex_L5_UPC.json' used by "
            "the following entries:\n\tSynthesisInputs: (brain_region=Isocortex ; mtype=L5_UPC ; "
            "luigi_config=luigi_Isocortex): "
            "distributions_path=distr_luigi_Isocortex_Isocortex_L5_UPC.json, "
            "parameters_path=params_luigi_Isocortex_Isocortex_L5_UPC.json"
        ),
        (
            "Rebuilding the file 'params_luigi_Isocortex_Isocortex_L5_UPC.json' used by "
            "the following entries:\n\tSynthesisInputs: (brain_region=Isocortex ; mtype=L5_UPC ; "
            "luigi_config=luigi_Isocortex): "
            "distributions_path=distr_luigi_Isocortex_Isocortex_L5_UPC.json, "
            "parameters_path=params_luigi_Isocortex_Isocortex_L5_UPC.json"
        ),
        "Removing the file 'distr_luigi_Isocortex_Isocortex_L5_UPC.json'",
        "Removing the file 'params_luigi_Isocortex_Isocortex_L5_UPC.json'",
    ]

    # Check that the JSON files are no longer empty
    with synthdb.input_tools.input_file_path(base_internal_element.parameters_path).open(
        "r", encoding="utf-8"
    ) as f:
        assert len(json.load(f)) == 1
    with synthdb.input_tools.input_file_path(base_internal_element.distributions_path).open(
        "r", encoding="utf-8"
    ) as f:
        assert len(json.load(f)) == 1


def test_rebuild_multiple_entries(internal_db_session, saved_db_session, mock_synthesis, caplog):
    """Test element rebuild."""
    primary_key = ("Isocortex", "L4_UPC", "luigi_Isocortex")
    base_internal_element = internal_db_session.get(
        synthdb.schema.SynthesisInputsTable, primary_key
    )

    # Update values of another entry to have duplicated values
    synthdb.input_tools.update_input(
        "Isocortex",
        "L5_UPC",
        "luigi_Isocortex",
        parameters_path=base_internal_element.parameters_path,
        distributions_path=base_internal_element.distributions_path,
    )

    # Remove the content of parameters and distributions files
    with synthdb.input_tools.input_file_path(base_internal_element.parameters_path).open(
        "w", encoding="utf-8"
    ) as f:
        json.dump({}, f)
    with synthdb.input_tools.input_file_path(base_internal_element.distributions_path).open(
        "w", encoding="utf-8"
    ) as f:
        json.dump({}, f)

    caplog.clear()
    caplog.set_level(logging.DEBUG)

    # Rebuild files
    synthdb.input_tools.rebuild_input(*primary_key)

    messages = [i for i in caplog.record_tuples if i[0] == "synthdb.input_tools"]

    assert [i[2] for i in messages[:4]] == [
        (
            "Rebuilding the file 'distr_luigi_Isocortex_Isocortex_L4_UPC.json' used by the "
            "following entries:"
            "\n\tSynthesisInputs: (brain_region=Isocortex ; mtype=L4_UPC ; "
            "luigi_config=luigi_Isocortex): "
            "distributions_path=distr_luigi_Isocortex_Isocortex_L4_UPC.json, "
            "parameters_path=params_luigi_Isocortex_Isocortex_L4_UPC.json"
            "\n\tSynthesisInputs: (brain_region=Isocortex ; mtype=L5_UPC ; "
            "luigi_config=luigi_Isocortex): "
            "distributions_path=distr_luigi_Isocortex_Isocortex_L4_UPC.json, "
            "parameters_path=params_luigi_Isocortex_Isocortex_L4_UPC.json"
        ),
        (
            "Rebuilding the file 'params_luigi_Isocortex_Isocortex_L4_UPC.json' used by the "
            "following entries"
            ":\n\tSynthesisInputs: (brain_region=Isocortex ; mtype=L4_UPC ; "
            "luigi_config=luigi_Isocortex): "
            "distributions_path=distr_luigi_Isocortex_Isocortex_L4_UPC.json, "
            "parameters_path=params_luigi_Isocortex_Isocortex_L4_UPC.json"
            "\n\tSynthesisInputs: (brain_region=Isocortex ; mtype=L5_UPC ; "
            "luigi_config=luigi_Isocortex): "
            "distributions_path=distr_luigi_Isocortex_Isocortex_L4_UPC.json, "
            "parameters_path=params_luigi_Isocortex_Isocortex_L4_UPC.json"
        ),
        "Removing the file 'distr_luigi_Isocortex_Isocortex_L4_UPC.json'",
        "Removing the file 'params_luigi_Isocortex_Isocortex_L4_UPC.json'",
    ]

    # Check that the JSON files are no longer empty
    with synthdb.input_tools.input_file_path(base_internal_element.parameters_path).open(
        "r", encoding="utf-8"
    ) as f:
        assert len(json.load(f)) == 1
    with synthdb.input_tools.input_file_path(base_internal_element.distributions_path).open(
        "r", encoding="utf-8"
    ) as f:
        assert len(json.load(f)) == 1


def test_remove(internal_db_session, saved_db_session):
    """Test element removal."""
    # Create a new element with the same inputs as an existing entry
    base_primary_key = ("Isocortex", "L4_UPC", "luigi_Isocortex")
    base_internal_element = internal_db_session.get(
        synthdb.schema.SynthesisInputsTable, base_primary_key
    )
    assert (synthdb.input_tools.INPUTS_DIR / base_internal_element.parameters_path).exists()
    assert (synthdb.input_tools.INPUTS_DIR / base_internal_element.distributions_path).exists()

    primary_key = ("test_region", "test_mtype", "luigi_Isocortex")
    synthdb.input_tools.create_input(
        *primary_key,
        parameters_path=base_internal_element.parameters_path,
        distributions_path=base_internal_element.distributions_path,
    )

    created_element = internal_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key)

    # Deleted the created input (here the files should not be deleted since they are still used by
    # the base entry)
    synthdb.input_tools.remove_input(*primary_key)

    # Check state
    assert internal_db_session.get(synthdb.schema.SynthesisInputsTable, primary_key) is None
    assert (synthdb.input_tools.INPUTS_DIR / created_element.parameters_path).exists()
    assert (synthdb.input_tools.INPUTS_DIR / created_element.distributions_path).exists()

    # Deleted the created input (here the files should not be deleted since they are still used by
    # the base entry)
    synthdb.input_tools.remove_input(*base_primary_key)

    # Check state
    assert internal_db_session.get(synthdb.schema.SynthesisInputsTable, base_primary_key) is None
    assert not (synthdb.input_tools.INPUTS_DIR / base_internal_element.parameters_path).exists()
    assert not (synthdb.input_tools.INPUTS_DIR / base_internal_element.distributions_path).exists()

    # Remove all inputs and check that all files are also removed
    for element in internal_db_session.query(synthdb.schema.SynthesisInputsTable).all():
        synthdb.input_tools.remove_input(element.brain_region, element.mtype, element.luigi_config)

    assert list(synthdb.input_tools.LUIGI_CONFIGS_DIR.iterdir()) == []
    assert list(synthdb.input_tools.INPUTS_DIR.iterdir()) == []


def test_list_inputs(internal_db_session, saved_db_session):
    """Test how DB elements are listed."""
    assert sorted(synthdb.input_tools.list_inputs()) == sorted(
        saved_db_session.query(synthdb.input_tools.SynthesisInputsTable).all()
    )

    assert sorted(synthdb.input_tools.list_inputs(brain_region="Isocortex")) == sorted(
        saved_db_session.query(synthdb.input_tools.SynthesisInputsTable)
        .filter(synthdb.input_tools.SynthesisInputsTable.brain_region == "Isocortex")
        .all()
    )

    assert sorted(synthdb.input_tools.list_inputs(mtype="L4_UPC")) == sorted(
        saved_db_session.query(synthdb.input_tools.SynthesisInputsTable)
        .filter(synthdb.input_tools.SynthesisInputsTable.mtype == "L4_UPC")
        .all()
    )

    assert sorted(synthdb.input_tools.list_inputs(luigi_config="luigi_Isocortex")) == sorted(
        saved_db_session.query(synthdb.input_tools.SynthesisInputsTable)
        .filter(synthdb.input_tools.SynthesisInputsTable.luigi_config == "luigi_Isocortex")
        .all()
    )

    assert sorted(
        synthdb.input_tools.list_inputs(brain_region="Isocortex", luigi_config="luigi_Isocortex")
    ) == sorted(
        saved_db_session.query(synthdb.input_tools.SynthesisInputsTable)
        .filter(synthdb.input_tools.SynthesisInputsTable.brain_region == "Isocortex")
        .filter(synthdb.input_tools.SynthesisInputsTable.luigi_config == "luigi_Isocortex")
        .all()
    )


def test_pull_inputs(tmpdir, internal_db_session, saved_db_session):
    """Test that DB inputs are properly pulled."""
    output_path = Path(tmpdir / "output")

    # Fresh pull
    synthdb.input_tools.pull_inputs(
        brain_region="Isocortex", luigi_config="luigi_Isocortex", output_path=output_path
    )
    new_inputs = list(output_path.iterdir())
    assert len(new_inputs) == 2 * len(
        synthdb.input_tools.list_inputs(brain_region="Isocortex", luigi_config="luigi_Isocortex")
    )

    # Overwrite inputs
    synthdb.input_tools.pull_inputs(
        brain_region="Isocortex", luigi_config="luigi_Isocortex", output_path=output_path
    )
    new_inputs = list(output_path.iterdir())
    assert len(new_inputs) == 2 * len(
        synthdb.input_tools.list_inputs(brain_region="Isocortex", luigi_config="luigi_Isocortex")
    )

    # Unknown input
    msg = "Could not retrieve any input for brain_region=UNKNOWN ; mtype=None ; luigi_config=None"
    with pytest.raises(ValueError, match=msg):
        synthdb.input_tools.pull_inputs(brain_region="UNKNOWN", output_path=output_path)

    # Concatenate inputs
    output_path = Path(tmpdir / "output_concatenate_Isocortex")
    synthdb.input_tools.pull_inputs(
        brain_region="Isocortex",
        luigi_config="luigi_Isocortex",
        output_path=output_path,
        concatenate=True,
    )
    new_inputs = list(output_path.iterdir())
    assert len(new_inputs) == 2

    with (output_path / "tmd_parameters.json").open("r", encoding="utf-8") as f:
        output_params = json.load(f)
    with (output_path / "tmd_distributions.json").open("r", encoding="utf-8") as f:
        output_distrs = json.load(f)

    assert output_distrs.keys() == output_params.keys()
    for region in output_distrs:
        assert output_distrs[region].keys() == output_params[region].keys()

    output_path = Path(tmpdir / "output_concatenate_All")
    synthdb.input_tools.pull_inputs(
        output_path=output_path,
        concatenate=True,
    )
    new_inputs = list(output_path.iterdir())
    assert len(new_inputs) == 2

    with (output_path / "tmd_parameters.json").open("r", encoding="utf-8") as f:
        output_params = json.load(f)
    with (output_path / "tmd_distributions.json").open("r", encoding="utf-8") as f:
        output_distrs = json.load(f)

    assert output_distrs.keys() == output_params.keys()
    for region in output_distrs:
        assert output_distrs[region].keys() == output_params[region].keys()

    # inned-only inputs
    output_path = Path(tmpdir / "output_inner_only_Isocortex")
    with pytest.raises(ValueError):
        synthdb.input_tools.pull_inputs(
            brain_region="Isocortex",
            luigi_config="luigi_Isocortex",
            output_path=output_path,
            inner_only=True,
            concatenate=True,
        )

    synthdb.input_tools.pull_inputs(
        brain_region="Isocortex",
        luigi_config="luigi_Isocortex",
        mtype="L1_DAC",
        output_path=output_path,
        inner_only=True,
    )

    with (output_path / "tmd_parameters_luigi_Isocortex_Isocortex_L1_DAC.json").open(
        "r", encoding="utf-8"
    ) as f:
        output_params = json.load(f)
    with (output_path / "tmd_distributions_luigi_Isocortex_Isocortex_L1_DAC.json").open(
        "r", encoding="utf-8"
    ) as f:
        output_distrs = json.load(f)

    assert "basal_dendrite" in output_params
    assert "basal_dendrite" in output_distrs


def test_validate_inputs(tmpdir, internal_db_session, saved_db_session):
    """Test that DB inputs are properly validated."""
    # Validate actual current inputs
    synthdb.input_tools.validate_inputs()

    # Update an input to make it invalid
    invalidated_input = internal_db_session.get(
        synthdb.schema.SynthesisInputsTable, ("Isocortex", "L4_UPC", "luigi_Isocortex")
    )

    params = synthdb.input_tools.load_internal_file(invalidated_input.parameters_path)
    params["Isocortex"]["L4_UPC"]["apical_dendrite"]["apical_distance"] = "INVALID TYPE"
    with open(
        synthdb.input_tools.INPUTS_DIR / invalidated_input.parameters_path, "w", encoding="utf-8"
    ) as f:
        json.dump(params, f)

    distrs = synthdb.input_tools.load_internal_file(invalidated_input.distributions_path)
    distrs["Isocortex"]["L4_UPC"]["apical_dendrite"]["num_trees"] = "INVALID TYPE"
    with open(
        synthdb.input_tools.INPUTS_DIR / invalidated_input.distributions_path, "w", encoding="utf-8"
    ) as f:
        json.dump(distrs, f)

    # Validate invalid inputs
    msg = (
        r"""The file .*/tmd_parameters_luigi_Isocortex_Isocortex_L4_UPC\.json is not valid for """
        r"""the mtype L4_UPC and region Isocortex for the following reason:
In \[apical_dendrite\]: Additional properties are not allowed \(.* were unexpected\)
In \[apical_dendrite->apical_distance\]: 'INVALID TYPE' is not of type 'number'

"""
        r"""The file .*/tmd_distributions_luigi_Isocortex_Isocortex_L4_UPC\.json is not valid for"""
        r""" the mtype L4_UPC and region Isocortex for the following reason:
In \[apical_dendrite\]: Additional properties are not allowed \(.* were unexpected\)
In \[apical_dendrite->num_trees\]: 'INVALID TYPE' is not of type 'object'"""
    )
    with pytest.raises(synthdb.input_tools.ValidationError, match=msg):
        synthdb.input_tools.validate_inputs()
