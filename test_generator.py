# Unit test for generate_org_mode_file function using pytest and mocking
import pytest
from unittest.mock import mock_open, patch
from generator import generate_org_mode_file


def test_generate_org_mode_file():
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

    mock = mock_open()
    with patch("builtins.open", mock):
        generate_org_mode_file(translation_pairs, "output.org")

    # Assert that the mock file was written with the expected content
    mock().write.assert_called()
    written_content = "".join(call[0][0] for call in mock().write.call_args_list)
    assert written_content == expected_output


if __name__ == "__main__":
    pytest.main()
