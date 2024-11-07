"""Tests for the synthdb.cli module."""

# pylint: disable=unused-argument
import json

import synthdb.cli


class TestInputs:
    """Tests for the CLI related to inputs."""

    def test_create(self, internal_db_session, saved_db_session, cli_runner):
        """Test the create CLI command."""
        other_primary_key = ["Isocortex", "L5_UPC", "luigi_Isocortex"]
        other_element = saved_db_session.get(synthdb.schema.SynthesisInputsTable, other_primary_key)

        result = cli_runner.invoke(
            synthdb.cli.cli,
            [
                "-vv",
                "synthesis-inputs",
                "create",
                "test_region",
                "luigi_Isocortex",
                "--mtype",
                "test_mtype",
                "--parameters-path",
                other_element.parameters_path,
                "--distributions-path",
                other_element.distributions_path,
            ],
        )
        print(result.output)
        assert result.exit_code == 0

    def test_update(self, internal_db_session, saved_db_session, cli_runner):
        """Test the update CLI command."""
        other_primary_key = ["Isocortex", "L5_UPC", "luigi_Isocortex"]
        other_element = saved_db_session.get(synthdb.schema.SynthesisInputsTable, other_primary_key)

        result = cli_runner.invoke(
            synthdb.cli.cli,
            ["synthesis-inputs", "update"]
            + other_primary_key
            + [
                "--parameters-path",
                other_element.parameters_path,
                "--distributions-path",
                other_element.distributions_path,
            ],
        )
        assert result.exit_code == 0

    def test_rebuild(self, internal_db_session, saved_db_session, mock_synthesis, cli_runner):
        """Test the rebuild CLI command."""
        result = cli_runner.invoke(
            synthdb.cli.cli,
            ["synthesis-inputs", "rebuild"]
            + [
                "--brain-region",
                "Isocortex",
                "--mtype",
                "L5_UPC",
                "--luigi-config",
                "luigi_Isocortex",
            ],
        )
        assert result.exit_code == 0

    def test_remove(self, internal_db_session, saved_db_session, cli_runner):
        """Test the remove CLI command."""
        result = cli_runner.invoke(
            synthdb.cli.cli,
            [
                "synthesis-inputs",
                "remove",
                "--brain-region",
                "Isocortex",
                "--mtype",
                "L4_UPC",
                "--luigi-config",
                "luigi_Isocortex",
            ],
        )
        assert result.exit_code == 0

    def test_list(self, internal_db_session, saved_db_session, cli_runner):
        """Test the list CLI command."""
        result = cli_runner.invoke(synthdb.cli.cli, ["synthesis-inputs", "list"])
        assert result.exit_code == 0

    def test_pull(self, tmpdir, internal_db_session, saved_db_session, cli_runner):
        """Test the pull CLI command."""
        result = cli_runner.invoke(
            synthdb.cli.cli,
            [
                "synthesis-inputs",
                "pull",
                "--mtype",
                "L4_UPC",
                "--output-path",
                str(tmpdir / "output"),
            ],
        )
        assert result.exit_code == 0

    def test_validate(self, internal_db_session, saved_db_session, cli_runner):
        """Test the validate CLI command."""
        result = cli_runner.invoke(synthdb.cli.cli, ["synthesis-inputs", "validate"])
        assert result.exit_code == 0


class TestMorphologyRelease:
    """Tests for the CLI related to morphology releases."""

    def test_create(self, internal_db_session, saved_db_session, test_release, cli_runner):
        """Test the create CLI command."""
        result = cli_runner.invoke(
            synthdb.cli.cli,
            [
                "-vv",
                "morphology-release",
                "create",
                test_release["name"],
                "--gpfs-path",
                test_release["gpfs_path"],
                "--pip-list",
                json.dumps(test_release["pip_list"]),
            ],
        )
        assert result.exit_code == 0

        # Test with missing gpfs_path argument
        result = cli_runner.invoke(
            synthdb.cli.cli,
            [
                "-vv",
                "morphology-release",
                "create",
                test_release["name"],
            ],
        )
        assert result.exit_code == 2

    def test_update(self, internal_db_session, saved_db_session, test_release_inserted, cli_runner):
        """Test the update CLI command."""
        result = cli_runner.invoke(
            synthdb.cli.cli,
            [
                "morphology-release",
                "update",
                test_release_inserted["name"],
                "--gpfs-path",
                "/new/path/on/gpfs",
            ],
        )
        assert result.exit_code == 0

    def test_remove(self, internal_db_session, saved_db_session, test_release_inserted, cli_runner):
        """Test the remove CLI command."""
        result = cli_runner.invoke(
            synthdb.cli.cli, ["morphology-release", "remove", test_release_inserted["name"]]
        )
        assert result.exit_code == 0

    def test_list(self, internal_db_session, saved_db_session, test_release_inserted, cli_runner):
        """Test the list CLI command."""
        result = cli_runner.invoke(synthdb.cli.cli, ["morphology-release", "list"])
        assert result.exit_code == 0
        assert "; pip_list" not in result.output

        result = cli_runner.invoke(
            synthdb.cli.cli, ["morphology-release", "list", "--with-pip-list"]
        )
        assert result.exit_code == 0
        assert "; pip_list" in result.output

    def test_entry_point(self, script_runner):
        """Test the entry point."""
        ret = script_runner.run("synthdb", "--version")
        assert ret.success
        assert ret.stdout.startswith("synthdb, version ")
        assert ret.stderr == ""
