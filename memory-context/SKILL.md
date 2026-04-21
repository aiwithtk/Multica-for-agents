---
name: memory-context
description: "The persistent memory layer of the pipeline. Manages recurring prospect data, hot topics, internal controversies to avoid, and session-to-session continuity."
risk: low
source: workspace
date_added: "2026-04-21"
---

# Memory Context (The Archive)

This skill provides the **Long-Term Memory** necessary for a professional operation. Without this, the agent is just a generic chatbot. With it, the agent becomes a strategic partner that recognizes recurring faces and avoids brand-damaging topics.

## 1. Storage Architecture (The Vault)

For maximum clarity and auditability ("Opérateur concret"), the memory is stored in a structured JSON directory:

-   `memory/prospects.json`: Database of recurring subscribers, their roles, previous objections, and current conversational state.
-   `memory/hot_topics.json`: List of topics currently gaining traction (double-down candidates).
-   `memory/black_list.json`: Specific controversies or "traps" the agent must never engage with.
-   `memory/interaction_logs.json`: A summary history of past session outputs to avoid repeating the same examples or frameworks.

## 2. Core Data Schemas

### A. Prospect Profile
Each recurring user (`PROSPECT`) should have a profile containing:
- `username`: Identifying handle.
- `last_state`: (OPEN, ACTIVE, PENDING, CONVERTED, DEAD).
- `key_objections`: List of frictions they've raised in the past.
- `qualification_tier`: (Low, Medium, High).

### B. Hot Topics & Controversies
A simple list used as a sanity check during response generation:
- **Hot Topics (+):** "AI agents for sales", "Dagster automation", "Multi-agent workflows".
- **Controversies (-):** "Crypto scams", "Unethical AI usage", "Generic AI hype".

## 3. Integration with the Pipeline

### Read Phase (youtube-reader)
- When scanning a thread, the reader queries `memory-context/prospects.json`.
- If a user is recognized, their **Priority** is automatically elevated to **HIGH**, regardless of their current intent signal.

### Reply Phase (youtube-responder)
- Before drafting a reply, the responder pulls the user profile and the `black_list`.
- **Validation Rule:** If the current thread touches a blacklisted topic, the responder generates a "DEAD/IGNORE" signal or a cold de-escalation response.
- **Continuity Rule:** The responder references past interactions (e.g., "Comme on en a parlé il y a deux semaines...") to build authority.

## 4. Maintenance & Audit

The memory layer should be audited periodically:
- **Transitioning to DEAD:** If a prospect in `PENDING` hasn't interacted in 30 days, move them to `DEAD` in the memory.
- **Topical Refresh:** Manually update the `hot_topics.json` after successful viral events.

---
> [!IMPORTANT]
> This skill is the "Truth Engine" of the brand. It prevents the agents from making contradictory statements across different sessions.
