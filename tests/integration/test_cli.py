from typer.testing import CliRunner

from cli.cli import app

runner = CliRunner()


def test_cli_parse_help() -> None:
    """Test that the CLI parser returns the correct help message when '--help' is passed."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


def test_cli_parse() -> None:
    """Test that the CLI parser returns the correct help message when '--help' is passed."""
    result = runner.invoke(app, ["de:Tisch\nen:Dish", "/tmp/1.txt"])
    assert result.exit_code == 0
    with open("/tmp/1.txt") as file:
        lines = file.readlines()
    assert any("en: Dish" in line for line in lines)
    assert any("de: Tisch" in line for line in lines)
