# cli.py: Command Line Interface for generating Anki org-mode file using Typer
import typer

from core.generator import generate_org_mode_file
from core.parser import parse_translation_pairs


def cli_parse(pair: str, output: str):
    """
    Generate an Anki-compatible org-mode file from a translation pair.

    Args:
        pair (str): Translation pair in the format 'en:table de:der Tisch'.
        output (str): Path to output org-mode file.
    """
    # Parse translation pairs
    translation_pairs = parse_translation_pairs(pair)

    # Generate org-mode file
    generate_org_mode_file(translation_pairs, output)
    print(f"Org-mode file '{output}' generated successfully.")


if __name__ == "__main__":
    typer.run(cli_parse)
