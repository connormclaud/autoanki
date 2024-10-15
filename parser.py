# Milestone 1: Core Parsing and File Generation Module
# This script allows users to input translation pairs and generates an org-mode file for Anki


def parse_translation_pairs(input_data):
    """
    Parses input data into translation pairs.
    Args:
        input_data (str): Input data containing translation pairs, formatted as "en: table de: der Tisch".
    Returns:
        list of tuples: List containing language keys and translations, e.g., [("en", "table"), ("de", "der Tisch")]
    """
    translation_pairs = []
    pairs = input_data.split('\n') if input_data else []
    for pair in pairs:
        lang_key, word = pair.split(':')
        translation_pairs.append((lang_key.strip(), word.strip()))
    return translation_pairs


if __name__ == "__main__":
    # Example input data
    input_data = "en: table\nde: der Tisch\nen: chair\nde: der Stuhl"

    # Parse translation pairs
    translation_pairs = parse_translation_pairs(input_data)
    print(translation_pairs)
