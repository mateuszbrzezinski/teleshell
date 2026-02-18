# TeleShell (CLI tool)

AI-driven Telegram automation and intelligence. Transform your Telegram channel noise into actionable summaries using LLMs.

## Features
- **Flexible Summaries**: Get summaries for today, yesterday, last N days, or since your last run.
- **AI-Powered**: Uses Google Gemini via LiteLLM for high-quality, configurable summaries.
- **CLI First**: Simple and powerful command-line interface.
- **Checkpointing**: Remembers where you left off.

## Quick Start
1. Clone the repository.
2. Install dependencies: `pip install -e ".[dev]"`
3. Copy `.env.example` to `.env` and fill in your API keys.
4. Copy `config.yaml.example` to `~/.teleshell/config.yaml` and add your favorite channels.
5. Run: `tshell summarize --time-window today`

## Development
- **Linting**: `ruff check .`
- **Formatting**: `black .`
- **Type Checking**: `mypy .`
- **Testing**: `pytest`
