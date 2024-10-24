from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from wiktionary.ipa_service import IPAService, WiktionaryAPI


@pytest.fixture
async def ipa_service():
    return WiktionaryAPI()


async def test_ipa_service_fetch_ipa_not_implemented() -> None:
    """Unit test to verify that the fetch_ipa method raises NotImplementedError in the abstract IPAService class."""
    ipa_service = IPAService()

    with pytest.raises(NotImplementedError, match="Subclasses should implement this!"):
        # IPAService is an abstract class
        await ipa_service.fetch_ipa("test")


@pytest.mark.asyncio
async def test_wiktionary_api_client_error_with_mocked_session_manager(ipa_service) -> None:
    """Unit test to cover the aiohttp.ClientError handling in WiktionaryAPI."""
    with patch(
        "wiktionary.ipa_service.SessionManager", new_callable=AsyncMock,
    ) as MockSessionManager:
        # Create a mocked session
        mock_session = MagicMock()

        MockSessionManager.get_session.return_value = mock_session
        # Simulate a ClientError when calling the get method
        mock_response = mock_session.get.return_value
        mock_response.__aenter__.return_value = mock_response
        mock_response.raise_for_status.side_effect = aiohttp.ClientError(
            "Test Client Error",
        )

        # Call the fetch_ipa method and verify error handling
        response = await ipa_service.fetch_ipa("test")

        # Assert that the response contains the expected error message
        assert response == "Error: Test Client Error"
