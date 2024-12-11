"""Define the DB schema."""
# pylint: disable=too-few-public-methods
from functools import total_ordering
from pathlib import Path

from sqlalchemy import Column
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

SQLITE_DB = Path(__file__).parent / "data" / "internal_db.sqlite"
DB_URL = f"sqlite:///{SQLITE_DB}"

engine = create_engine(DB_URL)
metadata = MetaData()
session = sessionmaker(bind=engine)()
Base = declarative_base(metadata=metadata)


def commit_and_vacuum():
    """Commit the current session and perform a VACUUM."""
    session.commit()
    session.execute(text("VACUUM"))


@total_ordering
class SynthesisInputsTable(Base):
    """The table used to store the input mappings."""

    __tablename__ = "synthesis_inputs"

    brain_region = Column(String, nullable=False, primary_key=True)
    """The brain region."""

    mtype = Column(String, nullable=False, primary_key=True)
    """The mtype."""

    luigi_config = Column(String, nullable=False, primary_key=True)
    """The luigi configuration file."""

    distributions_path = Column(String, nullable=False)
    """The path to the distributions file."""

    parameters_path = Column(String, nullable=False)
    """The path to the parameters file."""

    def __str__(self):
        """Return the string representation of the instance."""
        return (
            f"SynthesisInputs: (brain_region={self.brain_region} ; mtype={self.mtype} ; "
            f"luigi_config={self.luigi_config}): distributions_path={self.distributions_path}, "
            f"parameters_path={self.parameters_path}"
        )

    def __eq__(self, other):
        """Equal operator."""
        try:
            return (
                self.brain_region == other.brain_region
                and self.mtype == other.mtype
                and self.luigi_config == other.luigi_config
                and self.distributions_path == other.distributions_path
                and self.parameters_path == other.parameters_path
            )
        except AttributeError:
            return False

    def __lt__(self, other):
        """Less than operator."""
        try:
            return (
                self.brain_region,
                self.mtype,
                self.luigi_config,
                self.distributions_path,
                self.parameters_path,
            ) < (
                other.brain_region,
                other.mtype,
                other.luigi_config,
                other.distributions_path,
                other.parameters_path,
            )
        except AttributeError as exc:
            raise NotImplementedError(
                f"Can not compare an object of type '{self.__class__.__name__}' with an object of "
                f"type '{type(other).__name__}'"
            ) from exc


@total_ordering
class MorphologyReleaseTable(Base):
    """The table used to store the morphology release metadata."""

    __tablename__ = "morph_releases"

    name = Column(String, nullable=False, primary_key=True)
    """The name of the release."""

    gpfs_path = Column(String, nullable=False)
    """The path to the morphology release on GPFS."""

    pip_list = Column(String, nullable=False)
    """The result of the `pip list --format json` command."""

    luigi_config = Column(String, nullable=True)
    """The luigi configuration file."""

    def __str__(self):
        """Return the string representation of the instance."""
        return (
            f"MorphologyRelease: name={self.name}: gpfs_path={self.gpfs_path} ; "
            f"luigi_config={self.luigi_config} ; pip_list={self.pip_list}"
        )

    def __eq__(self, other):
        """Equal operator."""
        try:
            return (
                self.name == other.name
                and self.gpfs_path == other.gpfs_path
                and self.pip_list == other.pip_list
                and self.luigi_config == other.luigi_config
            )
        except AttributeError:
            return False

    def __lt__(self, other):
        """Less than operator."""
        try:
            return (self.name, self.gpfs_path, self.pip_list or [], self.luigi_config or "") < (
                other.name,
                other.gpfs_path,
                other.pip_list or [],
                other.luigi_config or "",
            )
        except AttributeError as exc:
            raise NotImplementedError(
                f"Can not compare an object of type '{self.__class__.__name__}' with an object of "
                f"type '{type(other).__name__}'"
            ) from exc
