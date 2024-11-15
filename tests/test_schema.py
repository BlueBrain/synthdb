"""Test functions from synthdb.schema."""

import pytest

import synthdb.schema


class TestInputs:
    """Tests for the CLI related to inputs."""

    def test_str_cast(self):
        """Test string representation of ORM object."""
        obj = synthdb.schema.SynthesisInputsTable(
            species="species",
            brain_region="brain_region",
            mtype="mtype",
            luigi_config="luigi_config",
            distributions_path="distributions_path",
            parameters_path="parameters_path",
        )

        assert str(obj) == (
            "SynthesisInputs: (species=species ; brain_region=brain_region ; mtype=mtype ; "
            "luigi_config=luigi_config): distributions_path=distributions_path, "
            "parameters_path=parameters_path"
        )

    def test_equal_operator(self):
        """Test string representation of ORM object."""
        obj_1 = synthdb.schema.SynthesisInputsTable(
            species="species",
            brain_region="brain_region",
            mtype="mtype",
            luigi_config="luigi_config",
            distributions_path="distributions_path",
            parameters_path="parameters_path",
        )

        obj_2 = synthdb.schema.SynthesisInputsTable(
            species="species",
            brain_region="brain_region",
            mtype="mtype",
            luigi_config="luigi_config",
            distributions_path="distributions_path",
            parameters_path="parameters_path",
        )

        assert obj_1 == obj_2

        assert obj_1 != 0

    def test_lt_operator(self):
        """Test string representation of ORM object."""
        obj_1 = synthdb.schema.SynthesisInputsTable(
            species="species",
            brain_region="brain_region",
            mtype="mtype",
            luigi_config="luigi_config",
            distributions_path="distributions_path",
            parameters_path="parameters_path",
        )

        obj_2 = synthdb.schema.SynthesisInputsTable(
            species="species",
            brain_region="zzzzzzzzz",
            mtype="mtype",
            luigi_config="luigi_config",
            distributions_path="distributions_path",
            parameters_path="parameters_path",
        )

        assert obj_1 < obj_2
        assert obj_1 <= obj_2
        assert obj_2 > obj_1
        assert obj_2 >= obj_1

        with pytest.raises(
            NotImplementedError,
            match=(
                "Can not compare an object of type 'SynthesisInputsTable' with an object of type "
                "'int'"
            ),
        ):
            assert obj_1 < 0


class TestMorphologyRelease:
    """Tests for the CLI related to morphology releases."""

    def test_str_cast(self, test_release):
        """Test string representation of ORM object."""
        obj = synthdb.schema.MorphologyReleaseTable(
            name=test_release["name"],
            gpfs_path=test_release["gpfs_path"],
            pip_list=test_release["pip_list"],
            luigi_config=test_release["luigi_config"],
        )

        assert str(obj) == (
            f"MorphologyRelease: name={test_release['name']}: gpfs_path={test_release['gpfs_path']}"
            f" ; luigi_config={test_release['luigi_config']} ; pip_list={test_release['pip_list']}"
        )

    def test_equal_operator(self, test_release):
        """Test equal operator of ORM object."""
        obj_1 = synthdb.schema.MorphologyReleaseTable(
            name=test_release["name"],
            gpfs_path=test_release["gpfs_path"],
            pip_list=test_release["pip_list"],
            luigi_config=test_release["luigi_config"],
        )
        obj_2 = synthdb.schema.MorphologyReleaseTable(
            name=test_release["name"],
            gpfs_path=test_release["gpfs_path"],
            pip_list=test_release["pip_list"],
            luigi_config=test_release["luigi_config"],
        )

        assert obj_1 == obj_2

        assert obj_1 != 0

    def test_equal_operator_none(self, test_release):
        """Test equal operator of ORM object with None attributes."""
        obj_1 = synthdb.schema.MorphologyReleaseTable(
            name=test_release["name"],
            gpfs_path=test_release["gpfs_path"],
            pip_list=None,
            luigi_config=None,
        )
        obj_2 = synthdb.schema.MorphologyReleaseTable(
            name=test_release["name"],
            gpfs_path=test_release["gpfs_path"],
            pip_list=None,
            luigi_config=None,
        )

        assert obj_1 == obj_2

    def test_lt_operator(self, test_release):
        """Test less than operator of ORM object."""
        obj_1 = synthdb.schema.MorphologyReleaseTable(
            name=test_release["name"],
            gpfs_path=test_release["gpfs_path"],
            pip_list=test_release["pip_list"],
            luigi_config=test_release["luigi_config"],
        )
        obj_2 = synthdb.schema.MorphologyReleaseTable(
            name="zzzzzzzzz",
            gpfs_path=test_release["gpfs_path"],
            pip_list=test_release["pip_list"],
            luigi_config=test_release["luigi_config"],
        )

        assert obj_1 < obj_2
        assert obj_1 <= obj_2
        assert obj_2 > obj_1
        assert obj_2 >= obj_1

        with pytest.raises(
            NotImplementedError,
            match=(
                "Can not compare an object of type 'MorphologyReleaseTable' with an object of type "
                "'int'"
            ),
        ):
            assert obj_1 < 0

    def test_lt_operator_none(self, test_release):
        """Test less than operator of ORM object with None attributes."""
        obj_1 = synthdb.schema.MorphologyReleaseTable(
            name=test_release["name"],
            gpfs_path=test_release["gpfs_path"],
            pip_list=test_release["pip_list"],
            luigi_config=test_release["luigi_config"],
        )
        obj_2 = synthdb.schema.MorphologyReleaseTable(
            name=test_release["name"],
            gpfs_path=test_release["gpfs_path"],
            pip_list=None,
            luigi_config=test_release["luigi_config"],
        )

        assert obj_1 > obj_2
        assert obj_1 >= obj_2
        assert obj_2 < obj_1
        assert obj_2 <= obj_1

        obj_3 = synthdb.schema.MorphologyReleaseTable(
            name=test_release["name"],
            gpfs_path=test_release["gpfs_path"],
            pip_list=test_release["pip_list"],
            luigi_config=None,
        )

        assert obj_1 > obj_3
        assert obj_1 >= obj_3
        assert obj_3 < obj_1
        assert obj_3 <= obj_1
