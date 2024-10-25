"""Module to fetch IPA transcriptions for words from Wiktionary.

Classes:
    IPAService (ABC): Abstract base class for IPA retrieval.
    WiktionaryAPI (IPAService): Fetches IPA transcriptions
        from Wiktionary based on the specified language.
"""

import logging
import time

from abc import ABC, abstractmethod
import aiohttp

from wiktionary.metrics import REQUEST_COUNT, REQUEST_LATENCY
from wiktionary.session_manager import SessionManager
from wiktionary.wikitext_extractor import WikitextDataExtractor

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class IPAService(ABC):
    """Abstract base class for fetching IPA transcriptions."""

    @abstractmethod
    async def fetch_ipa(self, word: str) -> list[str] | str:
        """Fetch the IPA transcription(s) for a given word."""


class WiktionaryIPA(IPAService):
    """Fetch IPA transcriptions for a given word from Wiktionary."""

    def __init__(
        self, language: str = "de", extractor: WikitextDataExtractor | None = None
    ) -> None:
        """Initialize WiktionaryIPA with a specified language and extractor."""
        self.language = language
        self.api_url = f"https://{language}.wiktionary.org/w/api.php"
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.extractor = extractor or WikitextDataExtractor()
        logging.info("Initialized WiktionaryAPI with language=%s", language)

    async def fetch_ipa(self, word: str) -> list[str] | str:
        """Fetch the IPA pronunciation(s) for a given word from Wiktionary.

        Args:
            word (str): The word to fetch IPA for.

        Returns:
            Union[List[str], str]: A list of IPA transcriptions or
            an error message if not found.

        """
        params = {"action": "parse", "format": "json", "page": word, "prop": "wikitext"}
        logging.debug("Fetching IPA for word='%s' with params=%s", word, params)

        REQUEST_COUNT.labels(api_name="wiktionary").inc()
        start_time = time.time()

        try:
            session = await SessionManager.get_session()
            async with session.get(self.api_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                logging.debug("Received data for word='%s': %s}", word, data)
                return self.extractor.extract_ipa(data, word)
        except aiohttp.ClientError as e:
            logging.exception("Client error while fetching IPA for '%s'", word)
            return f"Error: {e!s}"
        finally:
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(api_name="wiktionary").observe(duration)
