"""Unit tests for core.generator module."""

from unittest.mock import MagicMock, patch

import pytest

from core.generator import generate_org_mode_file


def test_generate_org_mode_file() -> None:
    """Tests generate_org_mode_file function."""
    translation_pairs = [
        ("en", "table"),
        ("de", "der Tisch"),
        ("en", "chair"),
        ("de", "der Stuhl"),
    ]
    expected_output = """
* en: table
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
** Translation
table

* de: der Tisch
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
** Translation
der Tisch

* en: chair
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
** Translation
chair

* de: der Stuhl
:PROPERTIES:
:ANKI_NOTE_TYPE: Basic
:END:
** Translation
der Stuhl

""".lstrip("\n")

    with patch("core.generator.pathlib.Path.open", autospec=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        generate_org_mode_file(translation_pairs, "output.org")

    # Assert that the mock file was written with the expected
    written_content = "".join(call[0][0] for call in mock_file.write.call_args_list)
    assert written_content == expected_output


if __name__ == "__main__":
    pytest.main()
