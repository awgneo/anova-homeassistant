"""Test configuration and mocks for Anova API."""

import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_ws_response():
    """Mock aiohttp websocket response."""
    mock_ws = AsyncMock()
    mock_ws.send_str = AsyncMock()
    mock_ws.close = AsyncMock()
    mock_ws.closed = False
    
    # Mocking async iterator requires a bit of setup
    # but we can test logic manually in individual tests if needed
    
    return mock_ws

@pytest.fixture
def mock_session(mock_ws_response):
    """Mock aiohttp ClientSession."""
    session = AsyncMock()
    session.ws_connect = AsyncMock(return_value=mock_ws_response)
    session.close = AsyncMock()
    return session
