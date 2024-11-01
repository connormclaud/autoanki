"""Transcribe a given sentence into IPA."""

import asyncio
import logging

from wiktionary.ipa_service import IPAService

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class FetchIPACommand:
    """Fetching of IPA transcriptions.

    Command pattern for getting IPA using an IPA service.
    """

    def __init__(self, api: IPAService, word: str) -> None:
        """Initialize command with specified IPA service and word."""
        self.api = api
        self.word = word

    async def execute(self) -> list[str] | str:
        """Delayed execution."""
        return await self.api.fetch_ipa(self.word)


class IPATranscriber:
    """Transcribes entire sentences into IPA using an IPA service."""

    def __init__(self, ipa_service: IPAService) -> None:
        """Initialize Transcriber with an IPA service."""
        self.ipa_service = ipa_service
        logging.info("Initialized IPATranscriber with provided IPA service")

    async def transcribe_sentence(self, sentence: str) -> str:
        """Transcribes a given sentence into IPA using an IPA service.

        Args:
            sentence (str): The sentence to transcribe.

        Returns:
            str: The IPA transcription of the sentence.

        """
        words = sentence.split()
        logging.info("Transcribing sentence: '%s'", sentence)
        commands = [FetchIPACommand(self.ipa_service, word) for word in words]
        tasks = [command.execute() for command in commands]
        results = await asyncio.gather(*tasks)
        transcriptions = []
        for word, ipa in zip(words, results, strict=False):
            if isinstance(ipa, list) and ipa:
                transcriptions.append(
                    ipa[0],
                )  # Use the first IPA transcription if available
                logging.info("Word '%s' transcribed as '%s'", word, ipa[0])
            else:
                transcriptions.append(
                    f"[{word}]",
                )  # If no IPA found, use the word itself as a placeholder
                logging.info("No IPA found for word '%s', using placeholder.", word)
        return " ".join(transcriptions)
