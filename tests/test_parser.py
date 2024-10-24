# Unit tests for parse_translation_pairs function using pytest
import pytest

from core.parser import parse_translation_pairs


def test_basic_input() -> None:
    input_data = "en: table\nde: der Tisch\nen: chair\nde: der Stuhl"
    expected_output = [
        ("en", "table"),
        ("de", "der Tisch"),
        ("en", "chair"),
        ("de", "der Stuhl"),
    ]
    assert parse_translation_pairs(input_data) == expected_output


def test_empty_input() -> None:
    input_data = ""
    expected_output = []
    assert parse_translation_pairs(input_data) == expected_output


def test_extra_spaces() -> None:
    input_data = "  en:  table  \n de:   der Tisch "
    expected_output = [("en", "table"), ("de", "der Tisch")]
    assert parse_translation_pairs(input_data) == expected_output


def test_multiple_languages() -> None:
    input_data = "en: table \nes: mesa \nde: der Tisch"
    expected_output = [("en", "table"), ("es", "mesa"), ("de", "der Tisch")]
    assert parse_translation_pairs(input_data) == expected_output


if __name__ == "__main__":
    pytest.main()
