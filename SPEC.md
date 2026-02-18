# TeleShell: Specification for Milestone 1 (CLI Summarizer)

## 1. Project Overview
This document outlines the detailed specification for the first milestone of TeleShell, an AI-driven CLI tool. The primary goal of this milestone is to provide users with the ability to generate AI-powered summaries of Telegram channel content directly from the command line.

## 2. User Persona
*   **Name:** CLI Power User / Information Seeker
*   **Needs:**
    *   Quickly grasp key information from multiple Telegram channels without reading every message.
    *   Ability to customize summary scope (specific channels, timeframes).
    *   Reliable and consistent output in the terminal.
*   **Technical Skill:** Comfortable with command-line interfaces.

## 3. Core CLI Commands
The main command for this milestone will be `tshell summarize`. It will support flexible options for channel selection and time windows.

### `tshell summarize`
**Description:** Generates an AI-powered summary of messages from specified Telegram channel(s) within a defined timeframe.

**Options:**
*   `-c, --channels <CHANNEL_NAMES/IDs>`: Specifies one or more Telegram channels to summarize. Accepts channel usernames (e.g., `@TechNews`) or numerical IDs. Multiple channels can be provided, separated by commas. If omitted, uses default channels defined in `config.yaml`.
*   `-t, --time-window <VALUE>`: Defines the period for summarization.
    *   `<N>h`: Last N hours (e.g., `24h` for last 24 hours).
    *   `<N>d`: Last N days (e.g., `3d` for last 3 days).
    *   `today`: Messages from the current calendar day (00:00 to now).
    *   `yesterday`: Messages from the previous calendar day.
    *   `since_last_run`: Messages since the last successful execution of `tshell summarize` for the given channel(s). This relies on checkpointing in `config.yaml`.
*   `-o, --output-format <FORMAT>`: (Future consideration, for now only console)
*   `-v, --verbose`: (Optional) Provides more detailed output, e.g., message count, channels processed.

**Example Usage:**
*   `tshell summarize --channels @TechNews,MyDevChannel --time-window 24h`
*   `tshell summarize --time-window since_last_run` (uses default channels)
*   `tshell summarize -c @CryptoAlerts -t yesterday`

## 4. Configuration
Configuration will be managed via `.env` file for sensitive credentials and `config.yaml` for user-definable settings and state.

### Telegram Authentication
*   During the first run of `tshell summarize` (or a dedicated `tshell login` command), if the Telegram session file does not exist or is invalid, the application will initiate an interactive CLI process:
    1.  Prompt the user for their phone number.
    2.  Prompt for the verification code sent by Telegram.
    3.  Upon successful authentication, Telethon will store the session file (`telegram.session`) in a dedicated, secure location (`~/.teleshell/telegram.session`), eliminating the need for re-authorization.

### `config.yaml`
**Location:** `~/.teleshell/config.yaml` (If not found, it can be created interactively or by copying `config.yaml.example` from the project root).
**Purpose:** Stores user preferences and state.
*   `default_channels`: A list of channel usernames/IDs to be used when `--channels` option is not provided.
*   `summary_config`:
    *   `length`: Configurable summary length. This will influence the prompt sent to the LLM. Default to `medium`.
        *   **`short`**: Aim for **1-3 concise sentences**. Emphasizes brevity, captures core message.
        *   **`medium`**: Aim for **4-7 sentences**. Provides a balanced overview, covering main points and some supporting details.
        *   **`long`**: Aim for **8-12 sentences**. Offers a more comprehensive summary, including key points, context, and important nuances.
        *   **Numerical Input (e.g., `5`):** Interpreted as an approximate **maximum sentence count**. The LLM will be instructed to provide a summary of "up to X sentences".
        *   **Behavior**: These are treated as **strong guidelines/suggestions** for the LLM. While the LLM will be instructed to adhere to them, perfect adherence cannot be guaranteed.
*   `prompt_templates`: A dictionary mapping prompt names/types to actual prompt strings. These can be overridden by the user. Default templates will be provided internally.
    *   **Available Placeholders**:
        *   `{{messages}}`: The concatenated text content of the Telegram messages to be summarized.
        *   `{{summary_length_guideline}}`: A textual instruction derived from `summary_config.length` (e.g., "in 1-3 concise sentences", "up to 5 sentences").
        *   `{{channel_name}}`: The name of the Telegram channel being summarized.
        *   `{{time_period}}`: A descriptive string of the time period being summarized (e.g., "messages from today", "content from the last 24 hours").
    *   **Example (default, internal template):**
        ```yaml
        prompt_templates:
          default_summary: |
            Summarize the following Telegram messages from the channel '{{channel_name}}'
            for the period '{{time_period}}'. Focus on key topics and highlights
            and provide the summary {{summary_length_guideline}}.

            Messages:
            {{messages}}
        ```
*   `checkpoints`: A dictionary storing the last processed message information for each summarized channel, used by `--time-window since_last_run`.
    *   **Structure:**
        ```yaml
        checkpoints:
          '@channel_username_or_id':
            last_message_id: 12345
            last_message_date: '2024-02-18T10:30:00Z' # Store date for flexibility
        ```
    *   **Behavior for `since_last_run`:** If `config.yaml` is empty, or a checkpoint for a specific channel using `--time-window since_last_run` does not exist, the application will **require** the user to provide an explicit `--time-window` (e.g., `today`, `24h`) and display an informative error message. It will not attempt to guess the timeframe.

### `.env`
**Location:** Project root.
**Purpose:** Securely store sensitive API credentials.
*   `TELEGRAM_API_ID`: Your Telegram API ID.
*   `TELEGRAM_API_HASH`: Your Telegram API Hash.
*   `GEMINI_API_KEY`: Your Google Gemini API Key.

## 5. AI Integration
*   **LLM Provider:** Google Gemini.
*   **Orchestration Library:** LiteLLM.
*   **Process:**
    1.  Fetch messages from Telegram using Telethon.
    2.  Pre-process messages (e.g., filter duplicates, handle media, extract text).
    3.  **Context Management:** For large time windows (e.g., several days, up to a week), messages will be strategically chunked to avoid LLM token limits. This may involve multi-stage summarization (summarizing chunks, then summarizing those summaries).
    4.  **Prompt Construction:** The application will load the appropriate prompt template from `config.yaml` (or use a default internal template). It will then populate the available placeholders:
        *   `{{messages}}`: Injected with the processed Telegram messages.
        *   `{{summary_length_guideline}}`: Dynamically generated string based on `summary_config.length` (e.g., "in 1-3 concise sentences" for `short`, "up to 5 sentences" for `5`).
        *   `{{channel_name}}`: Injected with the name of the channel being summarized.
        *   `{{time_period}}`: Injected with a descriptive string of the time period.
    5.  Call LiteLLM to interface with Google Gemini API for summarization, using the constructed prompt.
    6.  Receive and format the summary.
*   **Prompt Engineering:**
    *   Initial focus on a robust and effective summarization prompt, designed to extract key topics and highlights.
    *   Prompts are configurable via `config.yaml`, allowing users to fine-tune the summarization behavior without code changes.
    *   The `{{summary_length_guideline}}` placeholder provides dynamic adjustment based on user configuration.
    *   Iterative refinement of prompt templates will be an ongoing process to improve summary quality.

## 6. Output Format
Summaries will be printed to the console in a clear, human-readable format.
*   Each channel summary will be clearly separated.
*   Summary will be concise, focusing on key topics and highlights.
*   Error messages will be informative and user-friendly.

## 7. Project Structure and File Locations
This section defines the internal organization of the project and the expected locations for user-specific files on the system.

### Internal Project Structure
The project will follow a standard Python package structure:
```
teleshell/
├── src/
│   ├── __init__.py          # Python package initialization
│   ├── main.py              # Main CLI entry point (uses Click/Typer)
│   ├── config.py            # Handles config.yaml loading, saving, and defaults
│   ├── telegram_client.py   # Encapsulates Telegram API interactions via Telethon
│   ├── summarizer.py        # Contains AI summarization logic using LiteLLM
│   └── utils.py             # General utility functions (e.g., time parsing, error handling)
├── tests/
│   ├── __init__.py
│   ├── unit/                # Unit tests for individual components
│   ├── integration/         # Integration tests for API interactions (mocked/real)
│   └── e2e/                 # End-to-End tests for CLI commands
├── .github/                 # GitHub Actions workflows
│   └── workflows/
│       └── ci.yml           # CI workflow for linting, formatting, testing
├── .env.example             # Example .env file for environment variables
├── GEMINI.md                # Project-specific mandates and agent instructions
├── pyproject.toml           # Project metadata, dependencies, build configuration (Poetry/Hatch/setuptools)
├── README.md                # Project README file
└── config.yaml.example      # Example config.yaml file for user reference
```

### User-Specific File Locations
User-specific configuration, session data, and logs will be stored in a dedicated directory in the user's home directory to avoid polluting the project root or system-wide directories.
*   **Base Directory:** `~/.teleshell/`
*   **`~/.teleshell/config.yaml`:** User's main configuration file.
*   **`~/.teleshell/telegram.session`:** Telegram session file, managed by Telethon after initial authentication.
*   **`~/.teleshell/logs/`:** Directory for application log files.

## 8. Engineering Practices
To ensure code quality, maintainability, and reliability, the following engineering practices will be strictly adhered to:

### Test Strategy
A comprehensive testing strategy will be implemented, driven by **Test-Driven Development (TDD)** principles. This means that unit and integration tests will be designed and written *before* the production code, guiding the design and development process. E2E tests will be created in parallel with functionality to verify the full user flow.

*   **Unit Tests:** For all individual modules, functions, and logic components (e.g., argument parsing, config handling, time validation, result formatting, checkpoint logic).
    *   **Tool:** `pytest`.
*   **Integration Tests:** For interactions with external APIs (Telegram, LiteLLM/Gemini). These tests will use:
    *   **Mocks:** For external services to ensure fast and reliable tests that don't depend on live API availability.
    *   **Controlled Environment:** Limited tests with actual API calls (e.g., using test accounts/data) to verify connectivity and basic functionality.
    *   **Tool:** `pytest` with libraries like `unittest.mock` or `respx` for HTTP mocking.
*   **End-to-End (E2E) Tests:** For primary CLI scenarios (e.g., `tshell summarize -c @test_channel -t today`). These will simulate the full application lifecycle from command execution to output display.
    *   **Tool:** `pytest` in conjunction with `subprocess` or `Click`'s `CliRunner` for CLI interaction.

### CI/CD with GitHub Actions
GitHub Actions will be utilized for automated Continuous Integration (CI) to ensure code quality and prevent regressions.
*   **Workflow:** Automated checks on every `push` and `pull_request`.
*   **Secure Handling:** Leveraging GitHub Actions' context to securely manage secrets and environment variables (e.g., API keys required for integration tests).
*   **Checks:**
    *   **Linting & Formatting:** Running code style checks.
    *   **Test Execution:** Running all Unit, Integration, and E2E tests.

### Code Quality Tools
The following tools will be used to enforce code standards:
*   **`Black` (Formatter):** Automatically formats Python code to a consistent style, eliminating style debates.
*   **`Ruff` (Linter & Formatter):** A high-performance linter and formatter that combines the functionality of multiple tools (e.g., Flake8, isort). It will enforce best practices and catch potential errors.
*   **`Mypy` (Static Type Checker):** Performs static analysis of type hints to catch type-related bugs before runtime, enhancing code reliability and readability.

## 9. Dependencies
*   Python 3.9+
*   `telethon` (Telegram API client)
*   `litellm` (LLM orchestration)
*   `python-dotenv` (for loading `.env` files)
*   `pyyaml` (for `config.yaml` parsing)
*   `click` or `typer` (for CLI framework)
*   `pytest` (for testing)
*   `black` (for code formatting)
*   `ruff` (for linting)
*   `mypy` (for static type checking)

## 10. Future Enhancements (Roadmap - Beyond Milestone 1)
*   **Telegram Bot Integration:** Running TeleShell as a service/server, exposing functionality via a Telegram bot for interactive queries and scheduled reports.
*   **Advanced Prompt Engineering:** Dynamic prompt adjustments based on content, user preferences.
*   **Support for Multiple LLM Providers:** Easy switching between Gemini, OpenAI, Anthropic, etc., via configuration.
*   **Custom Output Formats:** Markdown files, JSON output, etc.

## 11. Acceptance Criteria (Milestone 1)
*   **Core Functionality:**
    *   User can run `tshell summarize -c <channel> -t <time-window>` where `<time-window>` is a flexible option (e.g., `24h`, `3d`, `today`, `yesterday`).
    *   User can run `tshell summarize -t since_last_run` (using default channels from `config.yaml`).
    *   Application correctly fetches messages from Telegram for the specified channels and timeframes.
    *   Application successfully generates a coherent, relevant, and configurable summary using Google Gemini via LiteLLM.
    *   Summary is clearly displayed in the console with appropriate formatting.
*   **Configuration & State Management:**
    *   `config.yaml` correctly updates `checkpoints` (last message ID and date) after `since_last_run` usage for each channel.
    *   `config.yaml` can be used to define `default_channels` and `summary_config.length`.
    *   All sensitive credentials (Telegram API ID/HASH, Gemini API Key) are loaded securely from `.env`.
*   **User Experience:**
    *   First-time Telegram authentication is handled via an interactive CLI prompt (asking for phone number and verification code), and a session file is securely stored in `~/.teleshell/telegram.session`.
    *   Informative error messages are displayed for invalid input (e.g., `time-window` format), missing channels, or API errors.
    *   When `since_last_run` is used without a prior checkpoint for a specific channel, the application will **require** the user to provide an explicit `--time-window` (e.g., `today`, `24h`) and display an informative error message.
*   **Code Quality & Testing:**
    *   All defined Unit, Integration, and E2E tests pass consistently.
    *   Code adheres to `Black` formatting and passes `Ruff` linting checks.
    *   Code passes `Mypy` static type checking.
    *   Project is installable via `pip install .` (or `pip install -e .` for development).
*   **CI/CD:**
    *   GitHub Actions workflow successfully runs linting, formatting checks, and all tests on `push` and `pull_request`.

---
*Status: Draft - Awaiting Stakeholder Review.*
