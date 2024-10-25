import pytest

from wiktionary.ipa_service import WiktionaryIPA
from wiktionary.session_manager import SessionManager
from wiktionary.transcriber import IPATranscriber


@pytest.mark.asyncio
async def test_transcribe_sentence_integration() -> None:
    """Integration test for transcribing a sentence using WiktionaryIPA and displaying the result."""
    # Example sentence transcription
    sentence = (
        "nach der Sache mit dem Buchp dachte ich es wäre doch möglich dass auch durch das Lachen "
        "manchmal mehr erreicht wird als durch das ständige Suchen nach einfachen Antworten doch"
    )

    # Create instances for the test
    ipa_service = WiktionaryIPA(language="de")
    transcriber = IPATranscriber(ipa_service=ipa_service)

    # Run transcription
    transcription = await transcriber.transcribe_sentence(sentence)

    # Close the aiohttp session
    await SessionManager.close_session()

    # Assert that transcription has valid content
    assert transcription is not None
    assert len(transcription) > 0
    assert transcription == (
        r"naːx deːɐ̯ ˈzaxə mɪt deːm [Buchp] ˈdaxtə ɪç ɛs ˈvɛːʁə dɔx"
        " ˈmøːklɪç das aʊ̯x dʊʁç das ˈlaxn̩ ˈmançmaːl meːɐ̯ ɛɐ̯ˈʁaɪ̯çt vɪʁt"
        " als dʊʁç das ˈʃtɛndɪɡə ˈzuːxn̩ naːx ˈaɪ̯nfaxn̩ ˈantˌvɔʁtn̩ dɔx"
    )
