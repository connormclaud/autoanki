import aiohttp
import asyncio
import re
import logging
import time
from typing import List, Union, Optional, Any
from prometheus_client import push_to_gateway
from wiktionary.session_manager import SessionManager
from wiktionary.metrics import REQUEST_COUNT, REQUEST_LATENCY, registry
from wiktionary.table_display import TranscriptionTableDisplay
from wiktionary.wikitext_extractor import WikitextDataExtractor

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class IPAService:
    async def fetch_ipa(self, word: str) -> Union[List[str], str]:
        raise NotImplementedError("Subclasses should implement this!")


class WiktionaryAPI(IPAService):
    def __init__(self, language: str = "de", extractor: Optional[Any] = None):
        self.language = language
        self.api_url = f"https://{language}.wiktionary.org/w/api.php"
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.extractor = extractor or WikitextDataExtractor()
        logging.info(f"Initialized WiktionaryAPI with language={language}")

    async def fetch_ipa(self, word: str) -> Union[List[str], str]:
        """
        Fetches the IPA pronunciation(s) for a given word from Wiktionary.

        Args:
            word (str): The word to fetch IPA for.

        Returns:
            Union[List[str], str]: A list of IPA transcriptions or an error message if not found.
        """
        params = {"action": "parse", "format": "json", "page": word, "prop": "wikitext"}
        logging.debug(f"Fetching IPA for word='{word}' with params={params}")

        REQUEST_COUNT.labels(api_name="wiktionary").inc()
        start_time = time.time()

        try:
            session = await SessionManager.get_session()
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
            REQUEST_LATENCY.labels(api_name="wiktionary").observe(duration)


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
                transcriptions.append(
                    ipa[0]
                )  # Use the first IPA transcription if available
                logging.info(f"Word '{word}' transcribed as '{ipa[0]}'")
            else:
                transcriptions.append(
                    f"[{word}]"
                )  # If no IPA found, use the word itself as a placeholder
                logging.info(f"No IPA found for word '{word}', using placeholder.")
        return " ".join(transcriptions)


if __name__ == "__main__":
    # Example sentence transcription
    sentence = (
        "nach der Sache mit dem Buch dachte ich es wäre doch möglich dass auch durch das Lachen "
        "manchmal mehr erreicht wird als durch das ständige Suchen nach einfachen Antworten doch"
    )

    # Run the transcription and display the results
    ipa_service = WiktionaryAPI(language="de")
    transcriber = IPATranscriber(ipa_service=ipa_service)
    transcription = asyncio.run(transcriber.transcribe_sentence(sentence))
    display = TranscriptionTableDisplay()
    display.display(sentence, transcription)

    # Close the aiohttp session
    asyncio.run(SessionManager.close_session())

    # Push the metrics to the Pushgateway
    push_to_gateway("localhost:9091", job="python_app", registry=registry)
