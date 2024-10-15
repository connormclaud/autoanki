import aiohttp
import asyncio
import re
import logging
import time
from prettytable import PrettyTable
from typing import List, Union, Optional, Any
from prometheus_client import Counter, Histogram, push_to_gateway, CollectorRegistry

# Configure logging to output to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

registry = CollectorRegistry()

# Prometheus metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total number of API requests', ['api_name'], registry=registry)
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'Latency of API requests', ['api_name'], registry=registry)


class AiohttpSessionSingleton:
    _session = None

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        if cls._session is None or cls._session.closed:
            cls._session = aiohttp.ClientSession()
        return cls._session

    @classmethod
    async def close_session(cls):
        if cls._session and not cls._session.closed:
            await cls._session.close()


class IPAService:
    async def fetch_ipa(self, word: str) -> Union[List[str], str]:
        raise NotImplementedError("Subclasses should implement this!")


class WiktionaryAPI(IPAService):
    def __init__(self, language: str = 'de', extractor: Optional[Any] = None):
        self.language = language
        self.api_url = f"https://{language}.wiktionary.org/w/api.php"
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.extractor = extractor or DataExtractor()
        logging.info(f"Initialized WiktionaryAPI with language={language}")

    async def fetch_ipa(self, word: str) -> Union[List[str], str]:
        """
        Fetches the IPA pronunciation(s) for a given word from Wiktionary.

        Args:
            word (str): The word to fetch IPA for.

        Returns:
            Union[List[str], str]: A list of IPA transcriptions or an error message if not found.
        """
        params = {
            'action': 'parse',
            'format': 'json',
            'page': word,
            'prop': 'wikitext'
        }
        logging.debug(f"Fetching IPA for word='{word}' with params={params}")

        REQUEST_COUNT.labels(api_name='wiktionary').inc()
        start_time = time.time()

        try:
            session = await AiohttpSessionSingleton.get_session()
            async with session.get(self.api_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                logging.debug(f"Received data for word='{word}': {data}")
                return self.extractor.extract_ipa(data, word)
        except aiohttp.ClientError as e:
            logging.error(f"Client error while fetching IPA for '{word}': {str(e)}")
            return f"Error: {str(e)}"
        finally:
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(api_name='wiktionary').observe(duration)


class DataExtractor:
    @staticmethod
    def extract_ipa(data: dict, word: str) -> Union[List[str], str]:
        wikitext = DataExtractor.get_nested(data, ['parse', 'wikitext', '*'])
        if wikitext:
            # Extract IPA in the immediate vicinity of the 'Aussprache' section
            aussprache_section = re.search(r'\{\{Aussprache\}\}(.+?)(\n\{|$)', wikitext, re.DOTALL)
            if aussprache_section:
                section_text = aussprache_section.group(1)
                ipa_matches = re.findall(r'\{\{IPA\|([^}]+)\}\}|\{\{Lautschrift\|([^}]+)\}\}', section_text)
                ipa_matches = [match for group in ipa_matches for match in group if match]  # Flatten matches
                if ipa_matches:
                    logging.info(f"Found IPA matches for word='{word}': {ipa_matches}")
                    return ipa_matches
        logging.info(f"No IPA found in Aussprache section for word='{word}'")
        return "No IPA found in Aussprache section."

    @staticmethod
    def get_nested(data: dict, keys: List[str], default: Any = '') -> Any:
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


class FetchIPACommand:
    def __init__(self, api: IPAService, word: str):
        self.api = api
        self.word = word

    async def execute(self) -> Union[List[str], str]:
        return await self.api.fetch_ipa(self.word)


class IPATranscriber:
    def __init__(self, ipa_service: IPAService):
        self.ipa_service = ipa_service
        logging.info(f"Initialized IPATranscriber with provided IPA service")

    async def transcribe_sentence(self, sentence: str) -> str:
        """
        Transcribes a given sentence into IPA using an IPA service.

        Args:
            sentence (str): The sentence to transcribe.

        Returns:
            str: The IPA transcription of the sentence.
        """
        words = sentence.split()
        logging.info(f"Transcribing sentence: '{sentence}'")
        commands = [FetchIPACommand(self.ipa_service, word) for word in words]
        tasks = [command.execute() for command in commands]
        results = await asyncio.gather(*tasks)
        transcriptions = []
        for word, ipa in zip(words, results):
            if isinstance(ipa, list) and ipa:
                transcriptions.append(ipa[0])  # Use the first IPA transcription if available
                logging.info(f"Word '{word}' transcribed as '{ipa[0]}'")
            else:
                transcriptions.append(f"[{word}]")  # If no IPA found, use the word itself as a placeholder
                logging.info(f"No IPA found for word '{word}', using placeholder.")
        return ' '.join(transcriptions)


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


if __name__ == '__main__':
    # Example sentence transcription
    sentence = (
        "nach der Sache mit dem Buch dachte ich es wäre doch möglich dass auch durch das Lachen "
        "manchmal mehr erreicht wird als durch das ständige Suchen nach einfachen Antworten doch"
    )

    # Run the transcription and display the results
    ipa_service = WiktionaryAPI(language='de')
    transcriber = IPATranscriber(ipa_service=ipa_service)
    transcription = asyncio.run(transcriber.transcribe_sentence(sentence))
    display = TranscriptionTableDisplay()
    display.display(sentence, transcription)

    # Close the aiohttp session
    asyncio.run(AiohttpSessionSingleton.close_session())


    # Push the metrics to the Pushgateway
    push_to_gateway('localhost:9091', job='python_app', registry=registry)
