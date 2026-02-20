# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.7] - 2026-02-19

### Added
- **Channel Titles:** Support for human-readable channel names (`Channel (@handle)`) throughout the UI and summaries.
- **Manual Titles:** New `--title` option for `tshell channels add` to manually set display names.
- **TUI Title Capture:** `tshell channels manage` now automatically fetches and persists channel titles from Telegram.

### Improved
- **AI Reliability:** Added built-in retry logic (up to 5 attempts) to handle model demand spikes (503 Service Unavailable).
- **Error Handling:** Graceful summarization failure handling—skips checkpoints if AI fails to prevent data loss.
- **UI Clarity:** Enhanced `tshell channels list` with better formatting and dimmed handles.

### Fixed
- **Config Cleanup:** `remove_channel` now correctly deletes associated channel titles from the configuration.

## [0.1.6] - 2026-02-19

### Fixed
- **TUI Stability:** Use `.execute_async()` to correctly run `InquirerPy` inside the existing event loop.
- **TUI Safety:** Added check for empty channel lists to prevent `ZeroDivisionError` during selection.
- **Channel Resolution:** Added support for numeric IDs passed as strings (e.g., in `config.yaml`), preventing `ValueError` during message fetching.
- **Config API:** Fixed `ConfigManager.save()` signature to correctly handle optional configuration dictionaries.

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
