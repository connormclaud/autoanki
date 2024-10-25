"""Extract information from Wiki text sources."""

import logging
import re
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class WikitextDataExtractor:
    """Class to extract data from Wiki text."""

    @staticmethod
    def extract_ipa(data: dict[str, Any], word: str) -> list[str] | str:
        """Extract IPA.

        (International Phonetic Alphabet) transcription from Wiki text.
        """
        wikitext = WikitextDataExtractor.get_nested(data, ["parse", "wikitext", "*"])
        if wikitext:
            # Extract IPA in the immediate vicinity of the 'Aussprache' section
            aussprache_section = re.search(
                r"\{\{Aussprache\}\}(.+?)(\n\{|$)",
                wikitext,
                re.DOTALL,
            )
            if aussprache_section:
                section_text = aussprache_section.group(1)
                ipa_matches = re.findall(
                    r"\{\{IPA\|([^}]+)\}\}|\{\{Lautschrift\|([^}]+)\}\}",
                    section_text,
                )
                ipa_matches = [
                    match for group in ipa_matches for match in group if match
                ]  # Flatten matches
                if ipa_matches:
                    logging.info(
                        "Found IPA matches for word='%s': %s", word, ipa_matches
                    )
                    return ipa_matches
        logging.info("No IPA found in Aussprache section for word='%s'", word)
        return "No IPA found in Aussprache section."

    @staticmethod
    def get_nested(data: dict, keys: list[str], default: str | None = "") -> str | None:
        """Safely retrieves a nested value from a dictionary.

        Args:
            data (dict): The dictionary to retrieve the value from.
            keys (List[str]): A list of keys representing the nested path.
            default (Any): The default value to return if the path is not found.

        Returns:
            Any: The value found at the nested path or the default value.

        """
        for key in keys:
            if data and isinstance(data, dict):
                data = data.get(key, default)
            if data == default:
                logging.debug("Key '%s' not found, returning default value.", key)
                return default
        return str(data) if data is not None else None
