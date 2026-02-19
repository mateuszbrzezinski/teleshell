# 📡 TeleShell

**TeleShell** is a powerful, AI-driven Python CLI tool for Telegram automation. It empowers you to intelligently summarize conversations, track channel activities, and extract key insights directly in your terminal using the latest Google Gemini models.

[![TeleShell CI](https://github.com/mateuszbrzezinski/teleshell/actions/workflows/ci.yml/badge.svg)](https://github.com/mateuszbrzezinski/teleshell/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

---

## ✨ Features

- 🤖 **AI-Driven Summarization:** Get intelligent summaries of any Telegram channel using `gemini-1.5-flash`.
- 🔍 **Precise Time Windows:** Summarize messages from "today", "yesterday", or specific durations like `24h` or `7d`.
- 💾 **Smart Checkpoints:** Track where you left off. TeleShell remembers the last processed message for each channel.
- 🎨 **Rich UI:** Beautifully formatted terminal output with Markdown rendering, progress bars, and high-contrast color schemes.
- 📊 **Performance Metrics:** Real-time feedback on message counts, token usage, and AI processing latency.
- 🛠️ **Developer Friendly:** Built with `uv`, `telethon`, and `litellm`. Fully typed and tested.

---

## 🚀 Quick Start

### 1. Installation
TeleShell is managed with `uv`. Clone the repository and sync dependencies:

```bash
git clone https://github.com/mateuszbrzezinski/teleshell.git
cd teleshell
uv sync --extra dev
```

### 2. Configuration
Create a `.env` file in the root directory (use `.env.example` as a template):

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
GEMINI_API_KEY=your_gemini_api_key
```

*Get your Telegram API credentials at [my.telegram.org](https://my.telegram.org) and your Gemini API key at [Google AI Studio](https://aistudio.google.com/).*

### 3. Usage Examples

#### Summarize a channel for the last 48 hours:
```bash
uv run tshell summarize -c @SwaperCom -t 48h
```

#### Summarize multiple channels since your last run:
```bash
uv run tshell summarize -c @SwaperCom,@TelegramNews -t since_last_run
```

#### Get a quick summary of what happened today:
```bash
uv run tshell summarize -c @SwaperCom -t today
```

---

## 🛠️ Commands & Options

| Option | Description | Default |
| :--- | :--- | :--- |
| `-c, --channels` | Comma-separated list of channel handles (e.g., `@SwaperCom`). | Required |
| `-t, --time-window` | Window to process: `today`, `yesterday`, `Xh`, `Xd`, or `since_last_run`. | `since_last_run` |
| `-v, --verbose` | Enable detailed logging for debugging. | `False` |

---

## 📈 Roadmap

- [ ] **Milestone 2:** Server Mode & Telegram Bot Integration.
- [ ] **Multi-Model Support:** Choose between Gemini, GPT-4, and Claude.
- [ ] **Custom Templates:** Define your own prompt templates for specialized summaries.
- [ ] **Export Options:** Save summaries to Markdown, PDF, or JSON.

---

## 🤝 Contributing

Contributions are welcome! Please read our `SPEC.md` to understand our development philosophy (Spec-Driven Development) before submitting a Pull Request.

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'feat: add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📜 License

Distributed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** License. This means you are free to share and adapt the material, but you **must give appropriate credit** and you **may not use the material for commercial purposes**.

See [LICENSE](LICENSE) for more information.

---
*Built with ❤️ by [Mateusz Brzeziński](https://github.com/mateuszbrzezinski)*
