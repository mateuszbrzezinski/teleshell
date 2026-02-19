from pathlib import Path
from typing import List, Dict, Any, Optional
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
                    if isinstance(f, DialogFilter):
                        # Use title for the folder, id is unique per user
                        folders[f.id] = f.title
            except Exception:
                # If folders cannot be fetched, we just return the default 'Main'
                pass
        return folders

    async def fetch_messages(
        self,
        channel: str,
        limit: Optional[int] = 1000,
        offset_id: int = 0,
        offset_date: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch messages from a specific Telegram channel.
        If offset_date is provided, fetches messages AFTER that date (newer).
        If offset_id is provided, fetches messages AFTER that ID.
        """
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

            messages = await self.client.get_messages(channel, **kwargs)

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
