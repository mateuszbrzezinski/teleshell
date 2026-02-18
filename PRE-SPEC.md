# TeleShell: Pre-Specification & Collaboration Charter

## 1. Project Identity
*   **Project Name:** TeleShell (CLI Tool)
*   **Mission:** AI-driven Telegram automation and intelligence.
*   **Core Goal:** Transforming Telegram channel noise into actionable summaries using LLMs.
*   **Roles:**
    *   **Stakeholder:** User (Product Vision, Requirements, Final Approval).
    *   **Lead Developer:** Gemini CLI (Research, Architecture, Spec-Driven Implementation, Verification).

## 2. Methodology: Spec-Driven Development (SDD)
To ensure reliability and alignment with the stakeholder's vision, we follow this strict cycle:
1.  **Discovery:** Brainstorming and gathering requirements (current phase).
2.  **Specification (SPEC.md):** Formalizing the "Truth". No code is written until the Spec is approved.
3.  **Planning:** Breaking down the Spec into technical tasks (Plan Mode).
4.  **Implementation:** Atomic code changes with immediate verification (Tests).
5.  **Review & Approval:** Stakeholder verifies the milestone.

## 3. Engineering Standards (AI-Driven Best Practices)
*   **Modular Architecture:** Separation of concerns (Telegram client, AI logic, CLI interface).
*   **Test-Driven Development (TDD):** Every feature must have a reproduction/verification script or unit test.
*   **Security First:** Use `.env` for secrets. Never log or commit Telegram session files or API keys.
*   **Idiomatic Python:** Adhering to PEP 8 and modern async patterns (Telethon).
*   **Core Technologies:** Python (programming language), Telethon (Telegram client), LiteLLM (AI orchestration library), Google Gemini (LLM provider).

## 4. Governance & Communication
*   **Decision Points:** Lead Dev proposes options; Stakeholder makes the final call on architectural or UX trade-offs.
*   **Incremental Progress:** Small, verifiable PR-like updates instead of massive code dumps.
*   **Backtracking:** If an implementation fails to meet the Spec, we revert to the Planning or Discovery phase.

## 5. Security & Privacy Protocol
*   **Local Execution:** TeleShell runs on the user's machine.
*   **Data Handling:** Telegram messages are processed only for the requested scope (summarization) and are not stored unless specified.

---
*Status: Draft - Awaiting Stakeholder Approval.*
