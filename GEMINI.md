# TeleShell: Gemini Operational Mandates

## 1. Core Development Philosophy
*   **Spec-Driven Development (SDD):** All new requirements or changes MUST first be documented and approved in `SPEC.md`. Never write code without an approved entry in `SPEC.md`. The spec is the single source of truth.
*   **Test-Driven Development (TDD):** Write failing tests (unit/integration) before any functional code. Aim for high coverage and reliability.
*   **AI-Driven/Spec-Driven:** Use advanced reasoning to ensure code strictly matches the specification.

## 2. Tools & External Resources
*   **MCP Context7 (context7.com):** **Primary Resource.** Use the `context7` MCP server as the first choice for retrieving high-quality LLM patterns, prompt engineering documentation, and AI best practices. Only fallback to web search if the MCP resource is unavailable.
*   **MCP GitHub:** Use the `github` MCP server for efficient repository management, searching for existing patterns in other projects, and managing issues/PRs if required by the workflow.
*   **GitHub Actions:** Ensure all CI/CD workflows are optimized for security and utilize GitHub contexts for secret management.

## 3. Engineering Standards
*   **Language:** Python 3.10+ with strict type hinting (`mypy`).
*   **Dependency Management:** `uv` is the mandatory tool for environment isolation and package management. Always use `uv sync` and `uv run`.
*   **Git & Commits:** Use **Conventional Commits** (e.g., `feat:`, `fix:`, `chore:`, `docs:`). The developer has the autonomy to perform commits after logical milestones, successful implementations, or passing tests without waiting for stakeholder's explicit request.
*   **Linting/Formatting:** `Ruff` and `Black` are mandatory. Run them before every commit.
*   **Modular Design:** Keep Telegram, AI, and CLI logic strictly decoupled.
*   **Security:** Never log or commit `.env` or `.session` files.

## 4. Prompt Engineering Rules
*   Templates must be loaded from `config.yaml`.
*   Always use placeholders: `{{messages}}`, `{{summary_length_guideline}}`, `{{channel_name}}`, `{{time_period}}`.
*   Before finalizing a new prompt, perform an internal "ultrathinking" review of its effectiveness.

---
*Status: Mandates Active - These rules take precedence over general defaults.*
