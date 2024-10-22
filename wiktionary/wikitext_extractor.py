from typing import Any
import re
import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class WikitextDataExtractor:
    @staticmethod
    def extract_ipa(data: dict, word: str) -> list[str] | str:
        wikitext = WikitextDataExtractor.get_nested(data, ["parse", "wikitext", "*"])
        if wikitext:
            # Extract IPA in the immediate vicinity of the 'Aussprache' section
            aussprache_section = re.search(
                r"\{\{Aussprache\}\}(.+?)(\n\{|$)", wikitext, re.DOTALL
            )
            if aussprache_section:
                section_text = aussprache_section.group(1)
                ipa_matches = re.findall(
                    r"\{\{IPA\|([^}]+)\}\}|\{\{Lautschrift\|([^}]+)\}\}", section_text
                )
                ipa_matches = [
                    match for group in ipa_matches for match in group if match
                ]  # Flatten matches
                if ipa_matches:
                    logging.info(f"Found IPA matches for word='{word}': {ipa_matches}")
                    return ipa_matches
        logging.info(f"No IPA found in Aussprache section for word='{word}'")
        return "No IPA found in Aussprache section."

    @staticmethod
    def get_nested(data: dict, keys: list[str], default: Any = "") -> Any:
        """
        Safely retrieves a nested value from a dictionary.

        Args:
            data (dict): The dictionary to retrieve the value from.
            keys (List[str]): A list of keys representing the nested path.
            default (Any): The default value to return if the path is not found.

        Returns:
            Any: The value found at the nested path or the default value.
        """
        for key in keys:
            data = data.get(key, default)
            if data == default:
                logging.debug(f"Key '{key}' not found, returning default value.")
                return default
        return data
