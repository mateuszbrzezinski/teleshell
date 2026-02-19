import click
import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional, List
from dotenv import load_dotenv

# Rich UI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from teleshell.config import ConfigManager
from teleshell.telegram_client import TelegramClientWrapper
from teleshell.summarizer import Summarizer

console = Console()


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
    channels: List[str], time_window: str, verbose: bool, config_manager: ConfigManager
) -> None:
    """Async core of the summarize command with optimized color scheme for readability."""
    load_dotenv()

    api_id = int(os.getenv("TELEGRAM_API_ID", 0))
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    if not api_id or not api_hash or not gemini_key:
        console.print(
            "[bold red]Error:[/bold red] Missing API credentials in .env file."
        )
        return

    config = config_manager.load()
    limit = 1000

    console.print("[bold cyan]📡 Connecting to Telegram...[/bold cyan]")
    tg_client = TelegramClientWrapper(api_id, api_hash)
    summarizer = Summarizer(api_key=gemini_key)

    await tg_client.start()

    for channel in channels:
        offset_date = None
        offset_id = 0
        since_label = ""

        if time_window == "since_last_run":
            checkpoint = config.get("checkpoints", {}).get(channel)
            if checkpoint:
                offset_id = checkpoint.get("last_message_id", 0)
                since_label = f"last run (ID: {offset_id})"
            else:
                console.print(
                    f"[bold yellow]⚠️ No checkpoint for {channel}.[/bold yellow] Please specify a time window (e.g., -t 24h)."
                )
                continue
        else:
            offset_date = parse_time_window(time_window)
            if not offset_date:
                console.print(
                    f"[bold red]❌ Invalid time window format:[/bold red] {time_window}"
                )
                return
            since_label = offset_date.strftime("%Y-%m-%d %H:%M")

        console.print(
            f"[bold white]🔍 Channel {channel}:[/bold white] Fetching messages since [cyan]{since_label}[/cyan] (Limit: {limit})..."
        )

        # Fetch limit + 1
        messages = await tg_client.fetch_messages(
            channel, limit=limit + 1, offset_id=offset_id, offset_date=offset_date
        )

        if not messages:
            console.print(f"[dim]ℹ️ No new messages found for {channel}.[/dim]")
            continue

        actual_count = len(messages)
        is_limited = actual_count > limit

        if is_limited:
            messages = messages[:limit]
            actual_count = limit

        newest_date = messages[0]["date"].strftime("%Y-%m-%d %H:%M")
        oldest_date = messages[-1]["date"].strftime("%Y-%m-%d %H:%M")

        if is_limited:
            console.print(
                f"[bold yellow]⚠️ Warning:[/bold yellow] Limit reached! Only {limit} messages fetched."
            )
            console.print(f"[yellow]Range: {oldest_date} to {newest_date}[/yellow]")
        else:
            console.print(
                f"[bold bright_blue]📥 Found {actual_count} messages[/bold bright_blue] (Range: {oldest_date} to {newest_date})."
            )

        console.print(
            f"[bold yellow]🤖 Generating AI summary using {summarizer.model}...[/bold yellow]"
        )

        result = await summarizer.summarize(
            messages=messages,
            channel_name=channel,
            time_period=f"{oldest_date} to {newest_date}",
            config=config.get("summary_config", {}),
            template=config.get("prompt_templates", {}).get("default_summary"),
        )

        summary_text = result["content"]
        meta = result["metadata"]

        # Rich Markdown Rendering
        md = Markdown(summary_text)
        console.print("\n")

        subtitle = (
            f"[dim]Analyzed: {actual_count} msgs | "
            f"Model: {meta.get('model', 'N/A')} | "
            f"Tokens: {meta.get('input_tokens', 0)}in/{meta.get('output_tokens', 0)}out | "
            f"Time: {meta.get('latency', 0)}s[/dim]"
        )

        console.print(
            Panel(
                md,
                title=f"[bold green]📡 TeleShell Summary: {channel}[/bold green]",
                subtitle=subtitle,
                border_style="green",
                padding=(1, 2),
            )
        )

        # Update checkpoint
        last_msg_id = messages[0]["id"]
        last_msg_date = messages[0]["date"].isoformat()
        config_manager.update_checkpoint(channel, last_msg_id, last_msg_date)
        console.print(f"[green]✅ Checkpoint updated for {channel}[/green]\n")


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """TeleShell: AI-driven Telegram automation and intelligence CLI tool."""
    ctx.ensure_object(dict)
    ctx.obj["config_manager"] = ConfigManager()


@cli.command()
@click.option("-c", "--channels", help="Channels to summarize (comma separated).")
@click.option("-t", "--time-window", default="since_last_run", help="Time period.")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output.")
@click.pass_context
def summarize(
    ctx: click.Context, channels: Optional[str], time_window: str, verbose: bool
) -> None:
    """Summarize Telegram channels within a defined timeframe."""
    config_manager = ctx.obj["config_manager"]
    config = config_manager.load()

    channel_list = []
    if channels:
        channel_list = [c.strip() for c in channels.split(",")]
    else:
        channel_list = config.get("default_channels", [])

    if not channel_list:
        console.print(
            "[bold red]Error:[/bold red] No channels provided and no default channels found in config.yaml."
        )
        return

    asyncio.run(run_summarize(channel_list, time_window, verbose, config_manager))


if __name__ == "__main__":
    cli()
