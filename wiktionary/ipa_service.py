import logging
import time
from typing import Any

import aiohttp

from wiktionary.metrics import REQUEST_COUNT, REQUEST_LATENCY
from wiktionary.session_manager import SessionManager
from wiktionary.wikitext_extractor import WikitextDataExtractor

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class IPAService:
    async def fetch_ipa(self, word: str) -> list[str] | str:
        msg = "Subclasses should implement this!"
        raise NotImplementedError(msg)


class WiktionaryAPI(IPAService):
    def __init__(self, language: str = "de", extractor: Any | None = None) -> None:
        self.language = language
        self.api_url = f"https://{language}.wiktionary.org/w/api.php"
        self.timeout = aiohttp.ClientTimeout(total=10)
        self.extractor = extractor or WikitextDataExtractor()
        logging.info(f"Initialized WiktionaryAPI with language={language}")

    async def fetch_ipa(self, word: str) -> list[str] | str:
        """Fetches the IPA pronunciation(s) for a given word from Wiktionary.

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
            logging.exception(f"Client error while fetching IPA for '{word}': {e!s}")
            return f"Error: {e!s}"
        finally:
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(api_name="wiktionary").observe(duration)
