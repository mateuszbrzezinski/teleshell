import click
import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional, List, Any, Dict
from dotenv import load_dotenv

# Rich UI
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# Interactive TUI
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator

from teleshell.config import ConfigManager
from teleshell.telegram_client import TelegramClientWrapper
from teleshell.summarizer import Summarizer, SummarizationError

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
    titles = config.get("channel_titles", {})

    console.print("[bold cyan]📡 Connecting to Telegram...[/bold cyan]")
    tg_client = TelegramClientWrapper(api_id, api_hash)
    summarizer = Summarizer(api_key=gemini_key)

    await tg_client.start()

    for channel in channels:
        title = titles.get(channel, channel)
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
                    f"[bold yellow]⚠️ No checkpoint for {title}.[/bold yellow] Please specify a time window (e.g., -t 24h)."
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
            f"[bold white]🔍 Channel {title}:[/bold white] Fetching messages since [cyan]{since_label}[/cyan] (Limit: {limit})..."
        )

        # Fetch limit + 1
        messages = await tg_client.fetch_messages(
            channel, limit=limit + 1, offset_id=offset_id, offset_date=offset_date
        )

        if not messages:
            console.print(f"[dim]ℹ️ No new messages found for {title}.[/dim]")
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

        try:
            result = await summarizer.summarize(
                messages=messages,
                channel_name=title,
                time_period=f"{oldest_date} to {newest_date}",
                config=config.get("summary_config", {}),
                template=config.get("prompt_templates", {}).get("default_summary"),
            )
        except SummarizationError as e:
            console.print(f"[bold red]❌ Summarization failed for {title}:[/bold red] {str(e)}")
            continue

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
                title=f"[bold green]📡 TeleShell Summary: {title}[/bold green]",
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


@cli.group()
def channels() -> None:
    """Manage tracked Telegram channels."""
    pass


@channels.command(name="list")
@click.pass_context
def list_channels(ctx: click.Context) -> None:
    """List currently tracked channels."""
    config_manager = ctx.obj["config_manager"]
    config = config_manager.load()
    tracked = config.get("default_channels", [])
    titles = config.get("channel_titles", {})

    if not tracked:
        console.print("[yellow]No channels currently tracked.[/yellow]")
        return

    console.print("[bold blue]Tracked Channels:[/bold blue]")
    for channel in tracked:
        title = titles.get(channel)
        if title:
            console.print(f" - {title} ([dim]{channel}[/dim])")
        else:
            console.print(f" - {channel}")


@channels.command(name="add")
@click.argument("handle")
@click.option("--title", help="Human-readable title for the channel.")
@click.pass_context
def add_channel(ctx: click.Context, handle: str, title: Optional[str]) -> None:
    """Add a channel to the tracked list."""
    config_manager = ctx.obj["config_manager"]
    config = config_manager.load()
    tracked = config.get("default_channels", [])

    if handle not in tracked:
        tracked.append(handle)
        config["default_channels"] = tracked
        
        if title:
            if "channel_titles" not in config:
                config["channel_titles"] = {}
            config["channel_titles"][handle] = title
            
        config_manager.save(config)
        console.print(f"[green]Added {handle} to tracking.[/green]")
    else:
        # Update title even if already tracked
        if title:
            if "channel_titles" not in config:
                config["channel_titles"] = {}
            config["channel_titles"][handle] = title
            config_manager.save(config)
            console.print(f"[green]Updated title for {handle}.[/green]")
        else:
            console.print(f"[yellow]{handle} is already tracked.[/yellow]")


@channels.command(name="remove")
@click.argument("handle")
@click.pass_context
def remove_channel(ctx: click.Context, handle: str) -> None:
    """Remove a channel from the tracked list."""
    config_manager = ctx.obj["config_manager"]
    config = config_manager.load()
    tracked = config.get("default_channels", [])
    titles = config.get("channel_titles", {})

    if handle in tracked:
        tracked.remove(handle)
        config["default_channels"] = tracked
        if handle in titles:
            del titles[handle]
        config_manager.save(config)
        console.print(f"[green]Removed {handle} from tracking.[/green]")
    else:
        console.print(f"[yellow]{handle} is not tracked.[/yellow]")


@channels.command(name="manage")
@click.pass_context
def manage_channels(ctx: click.Context) -> None:
    """Interactively manage tracked channels using a TUI."""
    load_dotenv()
    api_id = int(os.getenv("TELEGRAM_API_ID", 0))
    api_hash = os.getenv("TELEGRAM_API_HASH", "")

    if not api_id or not api_hash:
        console.print("[bold red]Error:[/bold red] TELEGRAM_API_ID/HASH missing in .env")
        return

def prepare_channel_choices(
    all_dialogs: List[Dict[str, Any]], folders: Dict[int, str], tracked: List[str]
) -> List[Any]:
    """
    Transform Telegram dialogs into InquirerPy Choice objects,
    grouped by folder separators and pre-selected if already tracked.
    """
    # Group by folder
    grouped: Dict[int, List[Dict[str, Any]]] = {}
    for d in all_dialogs:
        # Handle None as folder ID 0 (Main/Unsorted)
        f_id = d["folder_id"] if d["folder_id"] is not None else 0
        if f_id not in grouped:
            grouped[f_id] = []
        grouped[f_id].append(d)

    choices = []
    # Process folders in order (Main first, then others)
    sorted_folder_ids = sorted(grouped.keys(), key=lambda x: (x != 0, x))
    for f_id in sorted_folder_ids:
        folder_name = folders.get(f_id, "Main" if f_id == 0 else f"Folder {f_id}")
        choices.append(Separator(f"--- {folder_name} ---"))

        # Sort channels by title within folder
        folder_dialogs = sorted(grouped[f_id], key=lambda x: x["title"])
        for d in folder_dialogs:
            # Value will be the handle if available, otherwise ID
            value = d["handle"] if d["handle"] else str(d["id"])
            handle_display = f" (@{d['handle']})" if d["handle"] else f" (ID: {d['id']})"

            # Ultra-robust pre-selection check
            # Normalize tracked list: stringify, remove @, lowercase
            normalized_tracked = [str(t).lstrip("@").lower() for t in tracked]
            
            # Candidates for matching
            raw_id = str(d["id"])
            handle = d["handle"].lower() if d["handle"] else None
            
            is_enabled = (
                raw_id in normalized_tracked or
                (handle and handle in normalized_tracked)
            )

            choices.append(
                Choice(
                    value=(
                        f"@{value}" if d["handle"] and not value.startswith("@") else value
                    ),
                    name=f"{d['title']}{handle_display}",
                    enabled=is_enabled,
                )
            )
    return choices


@channels.command(name="manage")
@click.pass_context
def manage_channels(ctx: click.Context) -> None:
    """Interactively manage tracked channels using a TUI."""
    load_dotenv()
    api_id = int(os.getenv("TELEGRAM_API_ID", 0))
    api_hash = os.getenv("TELEGRAM_API_HASH", "")

    if not api_id or not api_hash:
        console.print("[bold red]Error:[/bold red] TELEGRAM_API_ID/HASH missing in .env")
        return

    config_manager = ctx.obj["config_manager"]
    config = config_manager.load()
    tracked = config.get("default_channels", [])

    tg_client = TelegramClientWrapper(api_id, api_hash)

    async def run_manage():
        with console.status(
            "[bold cyan]📡 Fetching your Telegram channels and folders...[/bold cyan]"
        ):
            await tg_client.start()
            all_dialogs = await tg_client.fetch_dialogs()
            folders = await tg_client.fetch_folders()

        choices = prepare_channel_choices(all_dialogs, folders, tracked)

        # Check for actual choices (excluding separators)
        has_choices = any(isinstance(c, Choice) for c in choices)
        if not has_choices:
            console.print(
                "[yellow]No channels or groups found on your Telegram account to manage.[/yellow]"
            )
            return

        selection = await inquirer.checkbox(
            message="Select channels to track (Space to toggle, Enter to confirm):",
            choices=choices,
            transformer=lambda result: f"{len(result)} channels selected",
        ).execute_async()

        if selection is not None:
            config["default_channels"] = selection
            
            # Update title mapping for selected channels
            if "channel_titles" not in config:
                config["channel_titles"] = {}
            
            # Build title lookup from all_dialogs
            title_lookup = {}
            for d in all_dialogs:
                val = f"@{d['handle']}" if d["handle"] else str(d["id"])
                title_lookup[val] = d["title"]
            
            for s in selection:
                if s in title_lookup:
                    config["channel_titles"][s] = title_lookup[s]

            config_manager.save(config)
            console.print(
                f"[bold green]✅ Success![/bold green] Updated tracking list with {len(selection)} channels."
            )

    asyncio.run(run_manage())


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
