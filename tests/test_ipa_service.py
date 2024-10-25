from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from wiktionary.ipa_service import WiktionaryIPA


@pytest.fixture
async def ipa_service():
    return WiktionaryIPA()


@pytest.mark.asyncio
async def test_wiktionary_api_client_error_with_mocked_session_manager(
    ipa_service,
) -> None:
    """Unit test to cover the aiohttp.ClientError handling in WiktionaryIPA."""
    with patch(
        "wiktionary.ipa_service.SessionManager",
        new_callable=AsyncMock,
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
