import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from telethon import TelegramClient
from telethon.tl.types import Message

class TelegramClientWrapper:
    """Wrapper around Telethon's TelegramClient for TeleShell needs."""

    def __init__(
        self, 
        api_id: int, 
        api_hash: str, 
        session_name: str = "telegram",
        base_dir: Optional[Path] = None
    ) -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        
        if not base_dir:
            base_dir = Path.home() / ".teleshell"
        
        base_dir.mkdir(parents=True, exist_ok=True)
        session_path = base_dir / f"{session_name}.session"
        
        self.client = TelegramClient(str(session_path), api_id, api_hash)

    async def fetch_messages(
        self, 
        channel: str, 
        limit: int = 100, 
        offset_id: int = 0,
        offset_date: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """Fetch messages from a specific Telegram channel."""
        messages_data = []
        async with self.client:
            messages = await self.client.get_messages(
                channel, 
                limit=limit, 
                offset_id=offset_id,
                offset_date=offset_date
            )
            
            for msg in messages:
                if isinstance(msg, Message):
                    messages_data.append({
                        "id": msg.id,
                        "text": msg.text or "",
                        "date": msg.date,
                        "sender_id": msg.sender_id
                    })
        
        return messages_data

    async def start(self) -> None:
        """Start the client and handle interactive login if necessary."""
        await self.client.start()
