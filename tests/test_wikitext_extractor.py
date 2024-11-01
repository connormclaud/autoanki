from wiktionary.wikitext_extractor import WikitextDataExtractor


def test_get_no_nested():
    result = WikitextDataExtractor.get_nested({}, ["nested"])
    assert result == str({}) == "{}"


def test_extract_no_ipa():
    wikitext = {"parse": {"wikitext": {"*": "{{Aussprache}}: IPA not matched."}}}
    result = WikitextDataExtractor.extract_ipa(wikitext, "test")
    assert result == "No IPA found in Aussprache section."


def test_extract_no_aussprache():
    wikitext = {"parse": {"wikitext": {"*": "{{Aussprache not matched}}: IPA."}}}
    result = WikitextDataExtractor.extract_ipa(wikitext, "test")
    assert result == "No IPA found in Aussprache section."
