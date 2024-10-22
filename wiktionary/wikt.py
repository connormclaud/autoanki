import asyncio
import logging
from typing import List, Union
from prometheus_client import push_to_gateway
from wiktionary.ipa_service import IPAService, WiktionaryAPI
from wiktionary.session_manager import SessionManager
from wiktionary.metrics import registry
from wiktionary.table_display import TranscriptionTableDisplay


# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
