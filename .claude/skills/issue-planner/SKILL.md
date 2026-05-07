---
name: issue-planner
description: "Plan, decompose, and create GitLab issues for this project. Use when the user wants to turn a vague idea or feature into a set of actionable issues, break a large issue into smaller vertical slices, create a single well-formed issue with proper structure, or plan a milestone's issue set. Triggers on phrases like 'plan issues for', 'create issues for', 'decompose this issue', 'break down', 'what issues do I need for', 'help me plan', 'let\u2019s plan the issues', or /issue-planner."
---

# Issue Planner

Three modes: **Plan** a feature into issues, **Decompose** a large issue, or **Create** a single issue. Read `references/best-practices.md` for detailed INVEST, vertical slicing, and label guidance.

## Codebase Research (before drafting any issue)

**Do not launch Explore agents. Read only what you need:**
1. CLAUDE.md is already loaded in the system prompt — do NOT re-read it
2. Read `start_work.py` — the entire application (~107 lines)

If something is still ambiguous, read `.env` or `requirements.txt` to resolve it. Stop there.

**Implementation details go in an issue comment, not the issue body.** When work begins on an issue, write a comment with file paths, specific methods to modify, and step-by-step approach. This keeps the issue body stable and avoids stale implementation notes.

---

## Mode 1 — Plan a Feature
*"Plan issues for X" / "What issues do I need for Y" / "Help me plan the notifications feature"*

1. **Clarify the goal** — If the idea is vague, ask one focused question to establish the user-facing outcome. Skip if already clear.

2. **Write the happy path** — Narrate what happens when the feature works end-to-end. Each distinct system interaction is a candidate issue or AC bullet.

3. **List failure modes** — For each happy-path step, what can go wrong? Non-trivial failures become issues; simple ones become AC bullets.

4. **Apply vertical slicing** — Cut through all layers (DB → handler → frontend) to produce thin, shippable issues. Never create issues for individual layers.

5. **Map dependencies** — Identify which issues must be done before others. Note any that can be done in parallel.

6. **Present the plan** — Show the full issue set in a table:

   | # | Title | Depends on | Labels |
   |---|-------|-----------|--------|
   | 1 | ... | — | feature, backend |
   | 2 | ... | #1 | feature, backend |

7. **Confirm before creating** — Ask: "Does this look right?" Do not create issues until confirmed.

8. **Create issues** — Use the `gitlab` skill to create each confirmed issue in dependency order.

---

## Mode 2 — Decompose a Large Issue
*"This issue is too big" / "Break down #12" / "Decompose PV-12"*

1. **Fetch the issue** — Use the `gitlab` skill to read the current issue content.

2. **Diagnose** — Check: title contains "and" for two concerns? AC has 8+ bullets? Spans 5+ unrelated areas? If none apply, tell the user the issue looks fine.

3. **Identify vertical slices** — Find the thinnest end-to-end slice that delivers something runnable. Make it issue 1. Build remaining capability on top.

4. **Present decomposition** — Show proposed sub-issues. Note what to do with the original (close? keep as epic description?).

5. **Confirm and create** — Get sign-off, then use the `gitlab` skill to create the new issues and update/close the original.

---

## Mode 3 — Create a Single Issue
*"Create an issue for X" / "Add an issue: ..."*

1. Draft using the template below.
2. Confirm milestone (ask user; list milestones via the `gitlab` skill if unknown).
3. Create using the `gitlab` skill.

---

## Issue Template

```markdown
## Context
<!-- Why does this exist? What problem does it solve? Link related issues. -->

## What to build
<!-- Precise description. For handler changes: trigger condition, filter, response format.
     For config changes: new .env variables and their purpose. -->

## Acceptance criteria
- [ ] Given <precondition>, when <action>, then <outcome>
- [ ] <error case 1>
- [ ] <error case 2>
- [ ] Tests cover happy path and at least one error path

## Out of scope
<!-- Explicitly list what this issue does NOT cover. -->

## How to test
<!-- IMPORTANT: Write specific steps for THIS issue — do not leave as a placeholder. -->
1. <precondition / setup>
2. <action>
3. <expected result>
```

---

## Issue Title Rules

| Pattern | Use for |
|---------|---------|
| `[Bug] <actual behaviour> when <condition>` | Bugs |
| `<Endpoint> <does what> when <condition>` | Backend API |
| `<User> can <do what>` | User-facing features |
| `<Component> <outcome>` | Infrastructure/chore |

**Good vs bad:**
```
✓  [Bug] Bot sends duplicate alerts when keyword appears twice in one message
✓  Bot monitors media messages with captions for keywords
✓  User can configure alert format via .env
✗  Fix alerts
✗  Update bot
```

---

## Acceptance Criteria

Written as **Given / When / Then** or verifiable checklist items. Cover: success, at least one error, auth check if applicable.

```
✓  Given a message containing "паблишер" in a monitored group, when the handler runs, then an alert is sent to TARGET_USER
✗  Errors are handled
✗  Tests pass
```

---

## Labels for This Project

| Group | Labels |
|-------|--------|
| Type (pick one) | `feature`, `bug` |

Always ask which milestone to assign. Milestones use 3-number semver format: `1.0.0`, `1.1.0`, `2.0.0`.

---

## Vertical Slicing Quick Reference

Cut **through** all layers per issue, never **across** layers:

```
✗ Horizontal (bad):          ✓ Vertical (good):
  Issue 1: Config parsing        Issue 1: Bot monitors new group for keywords
  Issue 2: Handler function      Issue 2: Bot detects media messages with captions
  Issue 3: Alert formatting      Issue 3: Bot sends alerts with message links
```

---

## References

See `references/best-practices.md` for:
- Full INVEST criteria with examples
- Epic decomposition walkthrough with a real example
- Prioritisation framework
- GitLab-specific tips (issue templates, scoped labels, board config, milestones)
- Comprehensive good vs bad examples table
