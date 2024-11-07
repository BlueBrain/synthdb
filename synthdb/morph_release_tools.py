"""Tools used to manage the morphology release metadatas."""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

from synthdb.schema import MorphologyReleaseTable
from synthdb.schema import session

MORPHOLOGY_RELEASES = Path(__file__).parent.resolve() / "morphology_releases"
LUIGI_CONFIGS_DIR = MORPHOLOGY_RELEASES / "luigi_configs"

LUIGI_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


def process_pip_list(pip_list=None):
    """Process a pip_list entry."""
    if pip_list is None or pip_list == "auto":
        env = {**os.environ, **{"PIP_YES": "true", "PIP_DISABLE_PIP_VERSION_CHECK": "true"}}
        pip_output = subprocess.check_output(
            [sys.executable, "-m", "pip", "list", "--format", "json"], env=env
        )
        pip_list = pip_output.decode()

    if not isinstance(pip_list, str):
        pip_list = json.dumps(pip_list)

    return pip_list


def check_luigi_config_exists(luigi_config):
    """Check that the given files exist in the repository."""
    if luigi_config is None:
        return None
    absolute_file = (LUIGI_CONFIGS_DIR / luigi_config).with_suffix(".cfg").absolute()
    if not absolute_file.exists():
        raise ValueError(f"The following file does not exist: {absolute_file}")
    return absolute_file.relative_to(LUIGI_CONFIGS_DIR).as_posix()


def create_release(release_name, gpfs_path, pip_list=None, luigi_config=None):
    """Create a new morphology release entry."""
    # Check that the given entry does not already exist
    selected_release = session.get(MorphologyReleaseTable, release_name)

    if selected_release is not None:
        raise ValueError(
            f"The following morphology release already exists: {selected_release.name}"
        )

    pip_list = process_pip_list(pip_list)
    luigi_config = check_luigi_config_exists(luigi_config)

    # Create the new entry in the DB
    new_obj = MorphologyReleaseTable(
        name=release_name,
        gpfs_path=gpfs_path,
        pip_list=pip_list,
        luigi_config=luigi_config,
    )

    session.add(new_obj)
    session.commit()

    logger.info("New element inserted in the DB: %s", new_obj)


def select_release(release_name):
    """Select and return a morphology release entry from the DB."""
    selected_release = session.get(MorphologyReleaseTable, release_name)

    if selected_release is None:
        raise ValueError(f"Could not retrieve the release named '{release_name}'")

    return selected_release


def update_release(release_name, gpfs_path=None, pip_list=None, luigi_config=None):
    """Update gpfs path or pip list of an entry in the DB."""
    selected_release = select_release(release_name)

    if gpfs_path is not None:
        selected_release.gpfs_path = gpfs_path
    if pip_list is not None:
        pip_list = process_pip_list(pip_list)
        selected_release.pip_list = pip_list
    if luigi_config is not None:
        selected_release.luigi_config = luigi_config

    session.commit()

    logger.info("Element updated in the DB: %s", selected_release)


def remove_release(release_name):
    """Remove the given morphology release entry from the DB."""
    selected_release = select_release(release_name)

    # Remove the entry from the DB
    session.delete(selected_release)
    session.commit()

    logger.info("Element removed from the DB: %s", selected_release)


def list_releases():
    """List all releases in the DB."""
    query = session.query(MorphologyReleaseTable)
    return query.all()
