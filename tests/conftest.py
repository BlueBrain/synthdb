"""Configuration for the pytest test suite."""
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
import json
import shutil
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from synthesis_workflow.tasks.synthesis import BuildSynthesisDistributions
from synthesis_workflow.tasks.synthesis import BuildSynthesisParameters

import synthdb.input_tools
import synthdb.morph_release_tools
import synthdb.schema


@pytest.fixture
def saved_db_path(tmpdir):
    """Path to the saved DB."""
    return Path(tmpdir / "saved_db.sqlite")


@pytest.fixture
def saved_db_url(saved_db_path):
    """URL of the saved DB."""
    return f"sqlite:///{saved_db_path}"


@pytest.fixture
def reset_db(tmpdir, saved_db_path):
    """Save the internal SQLite DB into a temporary directory and restore it after the test."""
    shutil.copy(synthdb.schema.SQLITE_DB, saved_db_path)
    shutil.copytree(
        str(synthdb.input_tools.SYNTHESIS_INPUTS),
        str(tmpdir / synthdb.input_tools.SYNTHESIS_INPUTS.name),
        dirs_exist_ok=True,
    )
    yield
    shutil.copy(saved_db_path, synthdb.schema.SQLITE_DB)
    shutil.copytree(
        str(tmpdir / synthdb.input_tools.SYNTHESIS_INPUTS.name),
        str(synthdb.input_tools.SYNTHESIS_INPUTS),
        dirs_exist_ok=True,
    )


@pytest.fixture
def saved_db_session(saved_db_url, reset_db):
    """Session to the saved DB."""
    engine = create_engine(saved_db_url)
    session = sessionmaker(bind=engine)()

    return session


@pytest.fixture
def internal_db_session(reset_db):
    """Session to the internal DB."""
    return synthdb.schema.session


@pytest.fixture
def test_release():
    """A test entry for a release."""
    luigi_config = synthdb.morph_release_tools.LUIGI_CONFIGS_DIR / "test_luigi.cfg"
    luigi_config.touch()
    yield {
        "name": "test_release",
        "gpfs_path": "/path/to/gpfs",
        "pip_list": [
            {
                "name": "package_1",
                "version": "1.2.3",
            },
            {
                "name": "package_2",
                "version": "0.0.0",
            },
        ],
        "luigi_config": "test_luigi.cfg",
    }
    luigi_config.unlink(missing_ok=True)


@pytest.fixture
def test_release_inserted(internal_db_session, test_release):
    """A test entry for a release which is already inserted in the DB."""
    new_obj = synthdb.schema.MorphologyReleaseTable(
        name=test_release["name"],
        gpfs_path=test_release["gpfs_path"],
        pip_list=json.dumps(test_release["pip_list"]),
    )
    internal_db_session.add(new_obj)
    internal_db_session.commit()
    return test_release


@pytest.fixture
def mock_synthesis(monkeypatch):
    """Mock synthesis process to not actually run it."""

    def _mock_distrs_reqs(*args, **kwargs):
        return

    def _mock_distrs_synthesis(*args, **kwargs):
        shutil.copy(
            str(
                synthdb.input_tools.SYNTHESIS_INPUTS
                / "inputs"
                / "distr_luigi_Isocortex_Isocortex_L6_UPC.json"
            ),
            str(
                synthdb.input_tools.TMP_OUT_DIR
                / "synthesis"
                / "neurots_input"
                / "tmd_distributions.json"
            ),
        )

    def _mock_params_reqs(*args, **kwargs):
        return

    def _mock_params_synthesis(*args, **kwargs):
        shutil.copy(
            str(
                synthdb.input_tools.SYNTHESIS_INPUTS
                / "inputs"
                / "params_luigi_Isocortex_Isocortex_L6_UPC.json"
            ),
            str(
                synthdb.input_tools.TMP_OUT_DIR
                / "synthesis"
                / "neurots_input"
                / "tmd_parameters.json"
            ),
        )

    monkeypatch.setattr(BuildSynthesisDistributions, "requires", _mock_distrs_reqs)
    monkeypatch.setattr(BuildSynthesisDistributions, "run", _mock_distrs_synthesis)
    monkeypatch.setattr(BuildSynthesisParameters, "run", _mock_params_synthesis)
    monkeypatch.setattr(BuildSynthesisParameters, "requires", _mock_params_reqs)
