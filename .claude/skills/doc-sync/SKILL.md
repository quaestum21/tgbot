---
name: doc-sync
description: Use AUTOMATICALLY before every git commit. Ensures CLAUDE.md stays in sync with code changes. Triggers when about to commit, stage changes, or when the user says "commit". MUST run before git commit — never commit without syncing docs first.
---

# Doc Sync

**Purpose:** Before every commit, update `CLAUDE.md` to reflect code changes. Only touch docs affected by the diff.

## Protocol

### Step 1: Identify changed files

Run `git diff --cached --name-only` to get staged files. If nothing is staged, run `git diff --name-only` instead.

Filter to relevant file types: `*.py`, `requirements.txt`

If no relevant files changed (e.g., only `.md`, `.env` values, or config files), **skip the update entirely** — proceed directly to commit.

### Step 2: Identify what needs updating in CLAUDE.md

Map changed files to the specific CLAUDE.md section that needs updating:

| Changed file pattern | CLAUDE.md section |
|----------------------|-------------------|
| `*.py` (new/removed/renamed handlers or functions) | Architecture section |
| `*.py` (new config variables added to loading section) | Configuration (.env) table |
| `requirements.txt` (new/removed dependencies) | Key Details (Dependencies line) |
| New `.py` files added | Architecture section (file structure) |

Only read `CLAUDE.md` if a match applies — do NOT read it on every commit.

### Step 3: Read and update

For each affected section:
1. `Read` the changed source file(s)
2. `Read` `CLAUDE.md`
3. Compare and `Edit` only the specific lines that need updating

**What to update:**
- New/removed/renamed handler functions or async functions
- New/changed `.env` variables in the Configuration table
- New/removed pip dependencies
- Changed line number references in the Architecture section
- Changed architecture (new files, split modules)

**What NOT to update:**
- Internal logic changes (bug fixes that don't change the architecture description)
- Comment or formatting changes
- Pure logic changes within existing functions

### Step 4: Stage the doc update

After editing, stage `CLAUDE.md` alongside the other changes. Same commit — no separate commit for docs.

### Step 5: Proceed to commit

Always draft and execute the commit yourself — never ask the user to run it. The commit message should NOT mention the doc sync — it's transparent.

## Rules

- NEVER skip this before a commit
- NEVER create a separate commit for doc updates — they go in the same commit
- If no docs need changes, don't touch them
- Keep the existing doc format and style exactly
- Use targeted `Read` + `Edit` — no Explore agents
