"""Integration test for CLI."""

from pathlib import Path
from typer.testing import CliRunner

from cli.cli import app

runner = CliRunner()


def test_cli_parse_help() -> None:
    """Test that the CLI parser returns the correct help message."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_cli_parse() -> None:
    """Test that the CLI generate org file."""
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
    result = runner.invoke(app, ["de:Tisch\nen:Dish", temp_file.name])
    assert result.exit_code == 0
    with Path(temp_file_path).open() as file:
        lines = file.readlines()
    assert any("en: Dish" in line for line in lines)
    assert any("de: Tisch" in line for line in lines)
