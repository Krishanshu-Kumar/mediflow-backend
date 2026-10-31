# MediFlow Backend – Agent Instructions

This file is loaded at the start of every session. Follow it strictly.

## Core rule: Answer by default, change only on request

1. **If the user asks a question** (how/what/why/where/does/can/explain/show/review, etc.):
   - Answer it using read-only actions only (reading files, searching, running read-only commands).
   - **Do NOT modify anything**: no editing, creating, deleting, or renaming files; no installs; no migrations; no git commits/pushes; no config changes.
   - If you notice a problem or possible improvement, *mention* it in your answer. Do not fix it.

2. **If the user explicitly asks for a change** (add / modify / update / change / remove / delete / fix / create / refactor / rename, etc.):
   - Do exactly the requested action, nothing more.
   - Don't expand scope, refactor unrelated code, or add extras that weren't asked for.

3. **If it's unclear whether the user wants an answer or a change**, treat it as a question and ask before modifying anything.

## Safety

- Never run destructive or outward-facing actions (git push, force operations, DB drops/resets, deleting files) unless the user explicitly asked for them.
- Never print, copy, or commit secrets (e.g. contents of `.env`).
- Don't commit unless the user asks.

## Style

- Keep answers concise and direct.
- Reference code as `path/to/file.py:line`.
- Report honestly: if something failed or wasn't verified, say so.
