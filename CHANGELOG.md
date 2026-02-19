# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - 2026-02-19

### Added
- **Interactive Management:** New `tshell channels manage` command with a full TUI.
- **Telegram Folders:** Support for grouping channels by your native Telegram folders.
- **Fuzzy Search:** Fast, real-time filtering of subscribed channels during selection.
- **TUI Controls:** Checkbox interface using `InquirerPy` (Space to toggle, Enter to save).
- **Sub-commands:** Added `tshell channels list`, `add`, and `remove` for fine-grained control.

### Changed
- Refactored `TelegramClientWrapper` to support dialog and filter discovery.
- Updated `pyproject.toml` with `inquirerpy` dependency.

### Fixed
- `TypeError` in channel management TUI when sorting folders containing `None` (unsorted) IDs.

## [0.1.0] - 2026-02-19

### Added
- **Core CLI:** First functional version of `tshell summarize` command.
- **Telegram Integration:** Secure authentication and message fetching using Telethon.
- **AI Summarization:** Integration with Google Gemini via LiteLLM for channel summaries.
- **Rich UI:** High-contrast terminal output with Markdown panels and progress reporting.
- **Usage Reporting:** Detailed metadata in summaries (token count, latency, model used).
- **Checkpoints:** Automatic tracking of last-processed message for seamless "since last run" updates.
- **Observability:** Accurate message counters with over-fetching to handle Telegram's global limit quirks.
- **Documentation:** Comprehensive `SPEC.md`, `README.md`, and `GEMINI.md` mandates.
- **CI/CD:** Automated testing and linting via GitHub Actions.
- **Legal:** Project licensed under Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).

### Fixed
- Chronological message fetching (forward instead of backward).
- Inaccurate global message counts from Telegram's `.total` attribute.
- CI failures related to Python version matrix and missing type stubs.

### Security
- Secrets management via `.env` and automatic session file protection.
- Removed sensitive data from git history and strengthened `.gitignore`.
