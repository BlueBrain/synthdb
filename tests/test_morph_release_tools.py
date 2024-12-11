"""Test functions from synthdb.morph_release_tools."""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
import json
import re
from pathlib import Path

import pytest

import synthdb.morph_release_tools
import synthdb.schema
from synthdb.schema import MorphologyReleaseTable


def test_select_release(internal_db_session, saved_db_session, test_release_inserted):
    """Test element selection."""
    base_element = synthdb.morph_release_tools.select_release(test_release_inserted["name"])
    assert base_element.name == test_release_inserted["name"]
    assert base_element.gpfs_path == test_release_inserted["gpfs_path"]
    assert base_element.pip_list == json.dumps(test_release_inserted["pip_list"])

    unknown_key = "UNKNOWN_RELEASE"
    msg = re.escape(f"Could not retrieve the release named '{unknown_key}'")
    with pytest.raises(ValueError, match=msg):
        synthdb.morph_release_tools.select_release(unknown_key)


def test_create_release(internal_db_session, saved_db_session, test_release):
    """Test element creation with given GPFS path and PIP list."""
    synthdb.morph_release_tools.create_release(
        release_name=test_release["name"],
        gpfs_path=test_release["gpfs_path"],
        pip_list=json.dumps(test_release["pip_list"]),
        luigi_config=test_release["luigi_config"],
    )

    created_element = internal_db_session.get(MorphologyReleaseTable, test_release["name"])
    assert created_element.gpfs_path == test_release["gpfs_path"]
    assert created_element.pip_list == json.dumps(test_release["pip_list"])
    assert created_element.luigi_config == test_release["luigi_config"]
    assert Path(synthdb.morph_release_tools.LUIGI_CONFIGS_DIR / created_element.luigi_config)


def test_create_automatic_pip_list(internal_db_session, saved_db_session, test_release):
    """Test element creation with given GPFS path and automatic PIP list creation."""
    synthdb.morph_release_tools.create_release(
        release_name=test_release["name"],
        gpfs_path=test_release["gpfs_path"],
    )

    created_element = internal_db_session.get(MorphologyReleaseTable, test_release["name"])
    assert created_element.gpfs_path == test_release["gpfs_path"]
    assert created_element.pip_list == synthdb.morph_release_tools.process_pip_list()


def test_create_existing(internal_db_session, saved_db_session, test_release_inserted):
    """Test element creation with an existing entry."""
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"The following morphology release already exists: {test_release_inserted['name']}"
        ),
    ):
        synthdb.morph_release_tools.create_release(
            release_name=test_release_inserted["name"],
            gpfs_path=test_release_inserted["gpfs_path"],
        )


def test_create_luigi_config_not_existing(internal_db_session, saved_db_session, test_release):
    """Test element creation with an existing entry."""
    expected_file = synthdb.morph_release_tools.LUIGI_CONFIGS_DIR / "NOT_EXISTING.cfg"
    with pytest.raises(
        ValueError,
        match=re.escape(f"The following file does not exist: {expected_file}"),
    ):
        synthdb.morph_release_tools.create_release(
            release_name=test_release["name"],
            gpfs_path=test_release["gpfs_path"],
            luigi_config="NOT_EXISTING",
        )


@pytest.fixture
def new_luigi_config():
    """A test entry for a release."""
    luigi_config = synthdb.morph_release_tools.LUIGI_CONFIGS_DIR / "new_test_luigi.cfg"
    luigi_config.touch()
    yield luigi_config.name
    luigi_config.unlink(missing_ok=True)


def test_update(internal_db_session, saved_db_session, test_release_inserted, new_luigi_config):
    """Test element update."""
    base_internal_element = internal_db_session.get(
        synthdb.schema.MorphologyReleaseTable, test_release_inserted["name"]
    )

    # Manually update values
    new_gpfs_path = "new_gpfs_path"
    new_pip_list = json.dumps([{"name": "test package", "version": "0.0.0"}])
    synthdb.morph_release_tools.update_release(
        test_release_inserted["name"],
        gpfs_path=new_gpfs_path,
        pip_list=new_pip_list,
        luigi_config=new_luigi_config,
    )

    # Check updated element
    updated_element = internal_db_session.get(
        synthdb.schema.MorphologyReleaseTable, test_release_inserted["name"]
    )
    assert updated_element.gpfs_path == new_gpfs_path
    assert updated_element.pip_list == new_pip_list
    assert updated_element.luigi_config == new_luigi_config

    # Update the parameter value automatically (should reset to initial value)
    synthdb.morph_release_tools.update_release(
        test_release_inserted["name"],
        gpfs_path=new_gpfs_path,
        pip_list="auto",
        luigi_config=new_luigi_config,
    )

    # Check updated element
    updated_element = internal_db_session.get(
        synthdb.schema.MorphologyReleaseTable, test_release_inserted["name"]
    )
    assert updated_element.gpfs_path == new_gpfs_path
    assert updated_element.pip_list == synthdb.morph_release_tools.process_pip_list()
    assert updated_element.luigi_config == new_luigi_config

    # Update only the gpfs_path values
    synthdb.morph_release_tools.update_release(
        test_release_inserted["name"],
        gpfs_path=test_release_inserted["gpfs_path"],
    )

    # Check updated element
    updated_element = internal_db_session.get(
        synthdb.schema.MorphologyReleaseTable, test_release_inserted["name"]
    )
    assert updated_element.gpfs_path == base_internal_element.gpfs_path
    assert updated_element.pip_list == synthdb.morph_release_tools.process_pip_list()
    assert updated_element.luigi_config == new_luigi_config

    # Update only the pip_list values
    synthdb.morph_release_tools.update_release(
        test_release_inserted["name"],
        pip_list=test_release_inserted["pip_list"],
    )

    # Check updated element
    updated_element = internal_db_session.get(
        synthdb.schema.MorphologyReleaseTable, test_release_inserted["name"]
    )
    assert updated_element.gpfs_path == base_internal_element.gpfs_path
    assert updated_element.pip_list == base_internal_element.pip_list
    assert updated_element.luigi_config == new_luigi_config

    # Update only the luigi_config values
    synthdb.morph_release_tools.update_release(
        test_release_inserted["name"],
        luigi_config=test_release_inserted["luigi_config"],
    )

    # Check updated element
    updated_element = internal_db_session.get(
        synthdb.schema.MorphologyReleaseTable, test_release_inserted["name"]
    )
    assert updated_element.gpfs_path == base_internal_element.gpfs_path
    assert updated_element.pip_list == base_internal_element.pip_list
    assert updated_element.luigi_config == base_internal_element.luigi_config


def test_remove(internal_db_session, saved_db_session, test_release_inserted):
    """Test element removal."""
    # Deleted the release
    synthdb.morph_release_tools.remove_release(test_release_inserted["name"])

    # Check state
    assert (
        internal_db_session.get(
            synthdb.schema.MorphologyReleaseTable, test_release_inserted["name"]
        )
        is None
    )

    # Try to delete a non existing release
    with pytest.raises(
        ValueError,
        match=re.escape(f"Could not retrieve the release named '{test_release_inserted['name']}'"),
    ):
        synthdb.morph_release_tools.remove_release(test_release_inserted["name"])


def test_list_releases(internal_db_session, saved_db_session, test_release_inserted):
    """Test how DB elements are listed."""
    assert sorted(i.name for i in synthdb.morph_release_tools.list_releases()) == sorted(
        i[0]
        for i in internal_db_session.query(
            synthdb.morph_release_tools.MorphologyReleaseTable.name
        ).all()
    )
