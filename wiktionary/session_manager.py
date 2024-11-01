"""Singleton for managing a reusable aiohttp ClientSession."""

import aiohttp


class AiohttpSessionSingleton:
    """Aiohttp Session Manager Singleton."""

    _session = None

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        """Get session or create if not exists."""
        if cls._session is None or cls._session.closed:
            cls._session = aiohttp.ClientSession()
        return cls._session

    @classmethod
    async def close_session(cls) -> None:
        """Close open session."""
        if cls._session and not cls._session.closed:
            await cls._session.close()
            cls._session = None

    @classmethod
    def has_session(cls) -> bool:
        """Return True if there is an existing session, otherwise False."""
        return cls._session is not None


SessionManager = AiohttpSessionSingleton
