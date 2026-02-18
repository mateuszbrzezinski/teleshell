import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from teleshell.telegram_client import TelegramClientWrapper
from telethon.tl.types import Message

@pytest.mark.asyncio
async def test_telegram_client_init():
    """Test if TelegramClientWrapper initializes correctly."""
    api_id = 12345
    api_hash = "test_hash"
    
    with patch("teleshell.telegram_client.TelegramClient") as mock_client:
        wrapper = TelegramClientWrapper(api_id, api_hash, session_name="test_session")
        assert wrapper.api_id == api_id
        assert wrapper.api_hash == api_hash
        mock_client.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_messages_success():
    """Test fetching messages from a channel."""
    api_id = 12345
    api_hash = "test_hash"
    
    with patch("teleshell.telegram_client.TelegramClient") as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        
        # Mock the async context manager and start method
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.start = AsyncMock()
        
        # Mock message objects using the real Message class as spec
        mock_msg = MagicMock(spec=Message)
        mock_msg.text = "Hello World"
        mock_msg.id = 1
        mock_msg.date = MagicMock()
        mock_msg.sender_id = 999
        
        # Mock get_messages to return a list of messages
        mock_client_instance.get_messages = AsyncMock(return_value=[mock_msg])
        
        wrapper = TelegramClientWrapper(api_id, api_hash)
        messages = await wrapper.fetch_messages("@test_channel", limit=10)
        
        assert len(messages) == 1
        assert messages[0]["text"] == "Hello World"
        assert messages[0]["id"] == 1
        mock_client_instance.get_messages.assert_called_once_with(
            "@test_channel", limit=10, offset_id=0, offset_date=None
        )
