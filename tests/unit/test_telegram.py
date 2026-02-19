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
    """Test fetching messages from a channel with the new logic."""
    api_id = 12345
    api_hash = "test_hash"

    with patch("teleshell.telegram_client.TelegramClient") as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        mock_msg = MagicMock(spec=Message)
        mock_msg.text = "Hello World"
        mock_msg.id = 1
        mock_msg.date = MagicMock()
        mock_msg.sender_id = 999

        mock_client_instance.get_messages = AsyncMock(return_value=[mock_msg])

        wrapper = TelegramClientWrapper(api_id, api_hash)
        messages = await wrapper.fetch_messages("@test_channel", limit=10)

        assert len(messages) == 1
        # In the new logic, we check min_id or offset_date in kwargs
        # but let's check that it was called with the basic limit at least
        args, kwargs = mock_client_instance.get_messages.call_args
        assert args[0] == "@test_channel"
        assert kwargs["limit"] == 10


@pytest.mark.asyncio
async def test_fetch_dialogs_success():
    """Test fetching dialogs (channels/groups)."""
    with patch("teleshell.telegram_client.TelegramClient") as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        
        # Mock a dialog with a channel entity
        mock_dialog = MagicMock()
        mock_dialog.name = "Test Channel"
        mock_dialog.id = 111
        mock_dialog.is_channel = True
        mock_dialog.is_group = False
        mock_dialog.entity = MagicMock()
        mock_dialog.entity.username = "test_handle"
        mock_dialog.dialog.folder_id = 1
        
        mock_client_instance.get_dialogs = AsyncMock(return_value=[mock_dialog])
        
        wrapper = TelegramClientWrapper(123, "hash")
        dialogs = await wrapper.fetch_dialogs()
        
        assert len(dialogs) == 1
        assert dialogs[0]["title"] == "Test Channel"
        assert dialogs[0]["handle"] == "test_handle"
        assert dialogs[0]["folder_id"] == 1


@pytest.mark.asyncio
async def test_fetch_dialogs_none_folder():
    """Test fetching dialogs with None folder_id (unsorted)."""
    with patch("teleshell.telegram_client.TelegramClient") as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        
        mock_dialog = MagicMock()
        mock_dialog.name = "No Folder Channel"
        mock_dialog.id = 222
        mock_dialog.is_channel = True
        mock_dialog.is_group = False
        mock_dialog.entity = MagicMock()
        mock_dialog.dialog.folder_id = None
        
        mock_client_instance.get_dialogs = AsyncMock(return_value=[mock_dialog])
        
        wrapper = TelegramClientWrapper(123, "hash")
        dialogs = await wrapper.fetch_dialogs()
        
        assert dialogs[0]["folder_id"] is None


@pytest.mark.asyncio
async def test_fetch_folders_success():
    """Test fetching Telegram folders (filters)."""
    with patch("teleshell.telegram_client.TelegramClient") as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        
        from telethon.tl.types import DialogFilter
        mock_filter = MagicMock(spec=DialogFilter)
        mock_filter.id = 2
        mock_filter.title = "Work"
        
        # client(...) call for GetDialogFiltersRequest
        mock_client_instance.return_value = [mock_filter]
        
        wrapper = TelegramClientWrapper(123, "hash")
        folders = await wrapper.fetch_folders()
        
        assert folders[0] == "Main"
        assert folders[2] == "Work"
