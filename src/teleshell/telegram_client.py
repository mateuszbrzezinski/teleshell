from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from telethon import TelegramClient, functions
from telethon.tl.types import Message, DialogFilter


class TelegramClientWrapper:
    """Wrapper around Telethon's TelegramClient for TeleShell needs."""

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session_name: str = "telegram",
        base_dir: Optional[Path] = None,
    ) -> None:
        self.api_id = api_id
        self.api_hash = api_hash

        if not base_dir:
            base_dir = Path.home() / ".teleshell"

        base_dir.mkdir(parents=True, exist_ok=True)
        session_path = base_dir / f"{session_name}.session"

        self.client = TelegramClient(str(session_path), api_id, api_hash)

    async def fetch_dialogs(self) -> List[Dict[str, Any]]:
        """Fetch all channels and megagroups the user is subscribed to."""
        dialogs = []
        async with self.client:
            # Get all dialogs (channels, groups, users)
            all_dialogs = await self.client.get_dialogs()
            for d in all_dialogs:
                # Filter for channels and megagroups
                if d.is_channel or d.is_group:
                    dialogs.append(
                        {
                            "id": d.id,
                            "title": d.name,
                            "handle": getattr(d.entity, "username", None),
                            "folder_id": getattr(d.dialog, "folder_id", 0),
                            "is_channel": d.is_channel,
                            "is_group": d.is_group,
                        }
                    )
        return dialogs

    async def fetch_folders(self) -> Dict[int, str]:
        """Fetch custom Telegram folders (filters) and their IDs."""
        folders = {0: "Main"}  # Default folder
        async with self.client:
            # Fetch user-defined folders (filters)
            try:
                filters = await self.client(functions.messages.GetDialogFiltersRequest())
                for f in filters:
                    # Use attribute checking for robustness and testability
                    if hasattr(f, "id") and hasattr(f, "title"):
                        # Use title for the folder, id is unique per user
                        folders[f.id] = f.title
            except Exception:
                # If folders cannot be fetched, we just return the default 'Main'
                pass
        return folders

    async def fetch_messages(
        self,
        channel: Union[str, int],
        limit: Optional[int] = 1000,
        offset_id: int = 0,
        offset_date: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch messages from a specific Telegram channel.
        If offset_date is provided, fetches messages AFTER that date (newer).
        If offset_id is provided, fetches messages AFTER that ID.
        """
        # Resolve numeric IDs passed as strings
        target = channel
        if isinstance(channel, str):
            # Check for digits or negative numbers (IDs)
            if channel.isdigit() or (channel.startswith("-") and channel[1:].isdigit()):
                try:
                    target = int(channel)
                except ValueError:
                    pass

        messages_data = []
        async with self.client:
            kwargs = {
                "limit": limit,
            }

            if offset_id > 0:
                kwargs["min_id"] = offset_id
            elif offset_date:
                kwargs["offset_date"] = offset_date
                kwargs["reverse"] = True

            try:
                messages = await self.client.get_messages(target, **kwargs)
            except ValueError:
                # If target is ID and not found, try to resolve entity first
                # This helps with small groups or old cached IDs
                try:
                    entity = await self.client.get_input_entity(target)
                    messages = await self.client.get_messages(entity, **kwargs)
                except Exception:
                    # Re-raise original if resolution fails
                    raise

            for msg in messages:
                if isinstance(msg, Message):
                    messages_data.append(
                        {
                            "id": msg.id,
                            "text": msg.text or "",
                            "date": msg.date,
                            "sender_id": msg.sender_id,
                        }
                    )

        # Sort newest first
        messages_data.sort(key=lambda x: x["id"], reverse=True)
        return messages_data

    async def start(self) -> None:
        """Start the client and handle interactive login if necessary."""
        await self.client.start()
