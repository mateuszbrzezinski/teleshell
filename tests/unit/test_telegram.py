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
        args, kwargs = mock_client_instance.get_messages.call_args
        assert args[0] == "@test_channel"
        assert kwargs["limit"] == 10


@pytest.mark.asyncio
async def test_fetch_dialogs_success():
    """Test fetching dialogs (channels/groups)."""
    with patch("teleshell.telegram_client.TelegramClient") as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

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
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

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
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)

        # Mock a folder-like object
        mock_filter = MagicMock()
        mock_filter.id = 2
        mock_filter.title = "Work"

        # Correct way to mock the client being called as a function (await client(...))
        mock_client_instance.side_effect = AsyncMock(return_value=[mock_filter])

        wrapper = TelegramClientWrapper(123, "hash")
        folders = await wrapper.fetch_folders()

        assert folders[0] == "Main"
        assert folders[2] == "Work"


@pytest.mark.asyncio
async def test_fetch_messages_numeric_id_string():
    """Test that numeric IDs passed as strings are resolved to integers."""
    with patch("teleshell.telegram_client.TelegramClient") as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client_instance.get_messages = AsyncMock(return_value=[])

        wrapper = TelegramClientWrapper(123, "hash")

        # Test negative ID string
        await wrapper.fetch_messages("-4750097632", limit=10)
        args, _ = mock_client_instance.get_messages.call_args
        assert args[0] == -4750097632
        assert isinstance(args[0], int)

        # Test positive ID string
        await wrapper.fetch_messages("123456", limit=10)
        args, _ = mock_client_instance.get_messages.call_args
        assert args[0] == 123456
        assert isinstance(args[0], int)

        # Test regular handle string remains string
        await wrapper.fetch_messages("@handle", limit=10)
        args, _ = mock_client_instance.get_messages.call_args
        assert args[0] == "@handle"
        assert isinstance(args[0], str)
