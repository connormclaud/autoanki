def generate_org_mode_file(translation_pairs, output_file) -> None:
    """Generates an org-mode file for Anki with the given translation pairs.

    Args:
        translation_pairs (list of tuples): List of translation pairs.
        output_file (str): Path to the output org-mode file.

    """
    with open(output_file, "w", encoding="utf-8") as f:
        for lang_key, word in translation_pairs:
            f.write(f"* {lang_key}: {word}\n")
            f.write(":PROPERTIES:\n:ANKI_NOTE_TYPE: Basic\n:END:\n")
            f.write(f"** Translation\n{word}\n\n")
