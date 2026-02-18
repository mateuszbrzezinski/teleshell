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
    """Async core of the summarize command with enhanced UX and observability."""
    load_dotenv()
    
    api_id = int(os.getenv("TELEGRAM_API_ID", 0))
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_id or not api_hash or not gemini_key:
        click.secho("Error: Missing API credentials in .env file.", fg="red")
        return

    config = config_manager.load()
    
    click.secho("📡 Connecting to Telegram...", fg="cyan")
    tg_client = TelegramClientWrapper(api_id, api_hash)
    summarizer = Summarizer(api_key=gemini_key)
    
    # Initialize Telegram session
    await tg_client.start()

    for channel in channels:
        offset_date = None
        offset_id = 0
        
        if time_window == "since_last_run":
            checkpoint = config.get("checkpoints", {}).get(channel)
            if checkpoint:
                offset_id = checkpoint.get("last_message_id", 0)
                click.secho(f"🔍 Channel {channel}: Fetching since last run (ID: {offset_id})...", fg="blue")
            else:
                click.secho(f"⚠️ No checkpoint for {channel}. Please specify a time window (e.g., -t 24h).", fg="yellow")
                continue
        else:
            offset_date = parse_time_window(time_window)
            if not offset_date:
                click.secho(f"❌ Invalid time window format: {time_window}", fg="red")
                return
            
            start_str = offset_date.strftime("%Y-%m-%d %H:%M")
            click.secho(f"🔍 Channel {channel}: Fetching messages since {start_str}...", fg="blue")

        messages = await tg_client.fetch_messages(
            channel, 
            limit=1000, 
            offset_id=offset_id, 
            offset_date=offset_date
        )
        
        if not messages:
            click.secho(f"ℹ️ No new messages for {channel}.", fg="white", dim=True)
            continue

        click.secho(f"📥 Found {len(messages)} messages. Preparing summary...", fg="blue")
        
        click.secho(f"🤖 Generating AI summary using {summarizer.model}...", fg="magenta")
        summary = await summarizer.summarize(
            messages=messages,
            channel_name=channel,
            time_period=time_window,
            config=config.get("summary_config", {}),
            template=config.get("prompt_templates", {}).get("default_summary")
        )
        
        # Display the summary in a rich format
        click.echo("\n" + "━" * 60)
        click.secho(f"📡 [TeleShell] {channel}", bold=True, fg="green")
        click.secho(f"📅 Period: {time_window}", dim=True)
        click.secho(f"📥 Analyzed: {len(messages)} messages", dim=True)
        click.echo("-" * 20)
        click.echo(summary)
        click.echo("━" * 60)
        
        # Update checkpoint with the latest message ID
        last_msg_id = messages[0]["id"]
        last_msg_date = messages[0]["date"].isoformat()
        config_manager.update_checkpoint(channel, last_msg_id, last_msg_date)
        click.secho(f"✅ Checkpoint updated for {channel} (Last ID: {last_msg_id})\n", fg="green", dim=True)

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
        click.secho("Error: No channels provided and no default channels found in config.yaml.", fg="red")
        return

    asyncio.run(run_summarize(channel_list, time_window, verbose, config_manager))

if __name__ == "__main__":
    cli()
