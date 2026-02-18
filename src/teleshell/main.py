import click
import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from teleshell.config import ConfigManager
from teleshell.telegram_client import TelegramClientWrapper
from teleshell.summarizer import Summarizer

def parse_time_window(window: str) -> Optional[datetime]:
    """Parse time window string into a start date."""
    now = datetime.now()
    if window == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif window == "yesterday":
        yesterday = now - timedelta(days=1)
        return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    elif window.endswith("h"):
        try:
            hours = int(window[:-1])
            return now - timedelta(hours=hours)
        except ValueError:
            return None
    elif window.endswith("d"):
        try:
            days = int(window[:-1])
            return now - timedelta(days=days)
        except ValueError:
            return None
    return None

async def run_summarize(
    channels: List[str], 
    time_window: str, 
    verbose: bool,
    config_manager: ConfigManager
) -> None:
    """Async core of the summarize command."""
    load_dotenv()
    
    api_id = int(os.getenv("TELEGRAM_API_ID", 0))
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_id or not api_hash or not gemini_key:
        click.echo("Error: Missing API credentials in .env file.")
        return

    config = config_manager.load()
    tg_client = TelegramClientWrapper(api_id, api_hash)
    summarizer = Summarizer(api_key=gemini_key)
    
    # Initialize Telegram session
    await tg_client.start()

    for channel in channels:
        if verbose:
            click.echo(f"Processing channel: {channel}...")
            
        offset_date = None
        offset_id = 0
        
        if time_window == "since_last_run":
            checkpoint = config.get("checkpoints", {}).get(channel)
            if checkpoint:
                offset_id = checkpoint.get("last_message_id", 0)
            else:
                click.echo(f"No checkpoint for {channel}. Please specify a time window (e.g., -t 24h).")
                continue
        else:
            offset_date = parse_time_window(time_window)
            if not offset_date:
                click.echo(f"Invalid time window format: {time_window}")
                return

        messages = await tg_client.fetch_messages(
            channel, 
            offset_id=offset_id, 
            offset_date=offset_date
        )
        
        if not messages:
            click.echo(f"No new messages for {channel}.")
            continue

        summary = await summarizer.summarize(
            messages=messages,
            channel_name=channel,
            time_period=time_window,
            config=config.get("summary_config", {}),
            template=config.get("prompt_templates", {}).get("default_summary")
        )
        
        click.echo(f"\nSummary for {channel}:")
        click.echo("-" * (12 + len(channel)))
        click.echo(summary)
        click.echo("-" * (12 + len(channel)))
        
        # Update checkpoint with the latest message ID
        last_msg_id = messages[0]["id"] # messages are usually returned newest first
        last_msg_date = messages[0]["date"].isoformat()
        config_manager.update_checkpoint(channel, last_msg_id, last_msg_date)

@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """TeleShell: AI-driven Telegram automation and intelligence CLI tool."""
    ctx.ensure_object(dict)
    ctx.obj['config_manager'] = ConfigManager()

@cli.command()
@click.option("-c", "--channels", help="Channels to summarize (comma separated).")
@click.option("-t", "--time-window", default="since_last_run", help="Time period.")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output.")
@click.pass_context
def summarize(ctx: click.Context, channels: Optional[str], time_window: str, verbose: bool) -> None:
    """Summarize Telegram channels within a defined timeframe."""
    config_manager = ctx.obj['config_manager']
    config = config_manager.load()
    
    channel_list = []
    if channels:
        channel_list = [c.strip() for c in channels.split(",")]
    else:
        channel_list = config.get("default_channels", [])
        
    if not channel_list:
        click.echo("Error: No channels provided and no default channels found in config.yaml.")
        return

    asyncio.run(run_summarize(channel_list, time_window, verbose, config_manager))

if __name__ == "__main__":
    cli()
