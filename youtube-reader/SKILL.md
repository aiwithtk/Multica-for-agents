---
name: youtube-reader
description: "Advanced conversation-aware input skill for YouTube pipelines. Features linear thread reconstruction, role-based metadata, and a 5-state lifecycle engine for high-signal conversion tracking."
risk: low
source: workspace
date_added: "2026-04-21"
---

# YouTube Reader (Conversation-Aware)

This skill is the **Intelligence Entry Point** for YouTube conversion pipelines. It transforms fragmented API threads into chronological conversations and tracks their business lifecycle.

## Prerequisites

- `youtube-automation` skill enabled.
- Active Rube MCP connection with `youtube` toolkit authorized.

## Business Logic: Conversation Over Data

### 1. Linear Chronological Reconstruction
API responses are fragmented. This skill mandates a "flattened" output format for every thread:
- **Format**: `[Timestamp] [Author] [Role]: Content`
- **Roles**:
    - `ME`: The channel owner (from `channelId`).
    - `PROSPECT`: An engaged user showing interest/objections.
    - `OTHER`: Bystanders, noise, or third-party interactions.

### 2. State Machine Logic
Threads are triaged into one of five business states:
1.  **OPEN**: Fresh comment with no creator response, or just initiated.
2.  **ACTIVE**: Reciprocal exchange. The prospect is actively replying and showing interest.
3.  **PENDING**: Creator has replied and is waiting for the prospect's next move.
4.  **CONVERTED**: Objective reached (e.g., link clicked, DM requested, explicit interest "merci je regarde").
5.  **DEAD**: No activity from the prospect for a defined period (default: 7-14 days).

### 3. Intent-Driven Priorities
Filter by intention, never by social metadata (likes):
- **Mentions (@)**: Priority **HIGH**. Direct attention request.
- **Questions (?)**: Priority **HIGH**. Information bridge.
- **Objections**: Priority **CRITICAL**. High-friction business signal.

## Workflows

### 1. Ingest & Flatten Conversations
**Goal**: Reconstruct human dynamics from API fragments.
1. Call `YOUTUBE_LIST_COMMENT_THREADS` (sorted by `time`).
2. For each thread, call `YOUTUBE_LIST_COMMENTS` for all replies.
3. **Flatten**: Sort parent and all replies by `publishedAt`.
4. **Annotate**: Assign `ME`, `PROSPECT`, or `OTHER` to each entry.

### 2. State & Intent Audit
**Goal**: Assign business value to the conversation.
1. Analyze the flattened thread for intent cues (?, objections, handle mentions).
2. Assign the appropriate state (`OPEN`, `ACTIVE`, etc.).
3. Update Priority level based on intent and state (e.g., `ACTIVE` + `OBJECTION` = `CRITICAL`).

### 3. Actionable Pipeline Output
**Goal**: Feed the next agent with actionable context.
- Output a list of threads in `OPEN` or `ACTIVE` states.
- Ensure the full flattened chronology is passed as the primary context.

## Pitfalls

- **Context Loss**: Never process a single comment without its thread history.
- **Dormant Threads**: Periodically audit `PENDING` threads to transition to `DEAD` if no response occurs.
- **API Quota**: Prioritize `ACTIVE` threads for full-reply fetching if quota is tight.

## When to Use
Use as the start of any workflow involving audience engagement, lead qualification, or brand reputation monitoring.
