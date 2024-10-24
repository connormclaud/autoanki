from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from wiktionary.session_manager import AiohttpSessionSingleton


@pytest.mark.asyncio
async def test_close_session_when_no_session_exists() -> None:
    """Test the close_session method when no session has been created."""
    # Ensure there is no existing session
    AiohttpSessionSingleton._session = None

    with patch("aiohttp.ClientSession.close", new_callable=AsyncMock) as mock_close:
        # Call close_session when no session exists
        await AiohttpSessionSingleton.close_session()

        # Ensure close was never called, as no session existed
        mock_close.assert_not_called()


@pytest.mark.asyncio
async def test_close_session_when_session_exists() -> None:
    """Test the close_session method when a session has been created."""
    # Create a mocked session
    mock_session = AsyncMock(spec=aiohttp.ClientSession)
    mock_session.closed = False

    AiohttpSessionSingleton._session = mock_session

    # Call close_session and ensure the session is closed
    await AiohttpSessionSingleton.close_session()
    mock_session.close.assert_called_once()

    # Ensure the session is set to None after closing
    assert AiohttpSessionSingleton._session is None
