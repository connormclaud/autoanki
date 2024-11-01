"""Unit tests for wikitext_extractor."""

from wiktionary.wikitext_extractor import WikitextDataExtractor


def test_get_no_nested() -> None:
    """Test no nested data."""
    result = WikitextDataExtractor.get_nested({}, ["nested"])
    assert result == str({}) == "{}"


def test_extract_no_ipa() -> None:
    """Test IPA pattern not found."""
    wikitext = {"parse": {"wikitext": {"*": "{{Aussprache}}: IPA not matched."}}}
    result = WikitextDataExtractor.extract_ipa(wikitext, "test")
    assert result == "No IPA found in Aussprache section."


def test_extract_no_aussprache() -> None:
    """Test Ausprache section not found."""
    wikitext = {"parse": {"wikitext": {"*": "{{Aussprache not matched}}: IPA."}}}
    result = WikitextDataExtractor.extract_ipa(wikitext, "test")
    assert result == "No IPA found in Aussprache section."
