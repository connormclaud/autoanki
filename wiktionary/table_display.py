import logging
from prettytable import PrettyTable

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AbstractTableDisplay:
    def display(self, sentence: str, transcription: str) -> None:
        table = PrettyTable()
        table.field_names = ["Word", "IPA"]
        self.fill_table(table, sentence, transcription)
        self.print_table(table)

    def fill_table(self, table: PrettyTable, sentence: str, transcription: str):
        raise NotImplementedError("Subclasses should implement this!")

    def print_table(self, table: PrettyTable):
        logging.info("\n" + table.get_string())


class TranscriptionTableDisplay(AbstractTableDisplay):
    def fill_table(self, table: PrettyTable, sentence: str, transcription: str):
        for word, ipa in zip(sentence.split(), transcription.split()):
            table.add_row([word, ipa])


