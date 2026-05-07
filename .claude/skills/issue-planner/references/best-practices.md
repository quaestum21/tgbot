# Issue Management Best Practices

## Table of Contents
1. [INVEST Criteria](#1-invest-criteria)
2. [Epic and Feature Decomposition](#2-epic-and-feature-decomposition)
3. [Planning — From Vague Idea to Actionable Issues](#3-planning)
4. [Labels, Milestones, and Estimates](#4-labels-milestones-and-estimates)
5. [GitLab-Specific Practices](#5-gitlab-specific-practices)
6. [Good vs Bad Examples](#6-good-vs-bad-examples)

---

## 1. INVEST Criteria

Every issue should pass INVEST before being picked up. Check each criterion.

| Letter | Criterion | What it means |
|--------|-----------|---------------|
| **I** | Independent | Can be built and deployed without waiting for another story |
| **N** | Negotiable | Implementation details are open; only the outcome is fixed |
| **V** | Valuable | Delivers observable value to a user or operator |
| **E** | Estimable | The team can size it; if not, it's too vague or too large |
| **S** | Small | Fits in 0.5–2 days of work for a solo dev |
| **T** | Testable | There is a concrete way to verify it's done |

**Applying INVEST to bot work:**

A handler change is "valuable" if it enables new monitoring, fixes missed alerts, or adds a new notification channel. It is "testable" if you can verify by sending a test message in a monitored group and checking the alert. Refactor issues must still justify value: "Reduces duplicate alerts by deduplicating messages" is valuable; "Refactor handler" is not.

---

## 2. Epic and Feature Decomposition

### Vertical vs Horizontal Slicing

**Horizontal (bad)** — cuts along technical layers:
```
Epic: Media message monitoring
  Issue 1: Add config parsing for media types
  Issue 2: Add Pyrogram filter
  Issue 3: Add handler function
  Issue 4: Update alert formatting
```
Nothing is runnable until issue 4.

**Vertical (good)** — cuts through all layers for a thin, shippable slice:
```
Epic: Media message monitoring
  Issue 1: Bot detects photo messages with captions containing keywords
  Issue 2: Bot detects document messages with captions containing keywords
  Issue 3: Bot detects forwarded messages containing keywords
  Issue 4: Bot includes message link in alert when available
```
After issue 1 you can run an end-to-end test. After issue 2 you have broader coverage.

### Right-Sizing Issues

| Size | Signals | Action |
|------|---------|--------|
| Too small | Single function change with no independent value | Merge into a related issue |
| Right | One coherent behaviour change; 0.5–2 days; one PR | Aim for this |
| Too large | Touches 5+ unrelated areas; 8+ AC bullets; title contains "and" | Split it |

### Epic Decomposition Workflow

1. Write the epic as a problem statement: *"Users need to be alerted when keywords are mentioned in media messages, not just text."*
2. List all capabilities implied. Write each as a user-facing outcome.
3. Find the thinnest vertical slice that produces something runnable. Make it issue 1.
4. Group remaining capabilities by dependency: which need issue 1 done first?
5. Identify anything truly independent (can be parallelised or deferred).
6. Each resulting issue should satisfy INVEST.

**Example — "Alert enrichment feature":**

Epic goal: Alerts include richer context — message links, reply threads, and sender history.

```
TMB-1  Alert includes direct link to the message in the group
TMB-2  Alert shows whether the message is a reply and includes parent message text
TMB-3  Alert includes count of recent messages from the same sender
TMB-4  Bot deduplicates alerts for the same message edited multiple times
```

TMB-1 is buildable and testable alone. TMB-2 adds orthogonal capability. TMB-3 is independent. TMB-4 prevents noise.

---

## 3. Planning

### From Vague Idea to Actionable Issues

**Step 1: Write the goal, not the solution**

One sentence: *"The bot should detect keyword mentions in photo captions and send alerts."*

**Step 2: Write the happy path narrative**

Walk through the system as if it already works. Note every interaction:
- User posts a photo with caption in a monitored group
- Bot receives the message via Pyrogram handler
- Bot checks caption text against keywords list
- Bot formats alert with group info, sender info, and caption text
- Bot sends alert to TARGET_USER

Each sentence is a candidate issue or AC bullet.

**Step 3: List failure modes**

For each happy-path step, what can go wrong?
- Photo has no caption → skip (no text to match)
- Caption is very long → truncate in alert
- Group has restricted message access → handler not triggered
- TARGET_USER has blocked the bot → send_message fails
- Rate limiting from Telegram API → delay between alerts

Non-trivial failures (like rate limiting) become separate issues. Most become AC bullets.

**Step 4: Draw the dependency graph**

For small features in this project: config changes → handler → alert formatting → CLAUDE.md update.

For small features, config and handler are usually bundled into one issue. Don't create separate issues for .env changes unless the config change is complex or shared by multiple features.

**Step 5: Sequence and assign**

Order issues so each builds on the last. Avoid situations where someone is blocked for more than a day.

### Identifying Dependencies

State dependencies explicitly in the issue description:
```
Depends on #1 (message link format must be established before reply thread context can reference it)
```

After creating issues in bulk, use GitLab's "blocks / is blocked by" relationship.

**Anti-patterns:**
- Circular dependencies (A blocks B blocks A) — split one
- Implicit dependencies — the next dev discovers them at implementation time
- False dependencies — verify before marking

### Prioritisation

| Priority | Meaning |
|----------|---------|
| `priority::critical` | Blocks release or breaks production |
| `priority::high` | Must be in current milestone to meet goal |
| `priority::medium` | Should be in milestone but can slip |
| `priority::low` | Nice to have; only pick up when high/medium are done |

Prioritise highest-value, highest-risk work first.

---

## 4. Labels, Milestones, and Estimates

### Label Taxonomy

Keep labels small and meaningful. Every label should influence a decision (what to work on next, who picks it up, what blocks release). If a label never affects a decision, delete it.

**Recommended for this project:**

```
Type (mutually exclusive)
  feature   — New capability
  bug       — Something broken that was working
  chore     — Infrastructure, refactor, dependency update (no user-visible change)
  docs      — Documentation only
```

**Anti-patterns:**
- Labels that duplicate board columns
- Labels with no clear definition
- More than 4–5 priority levels
- Labels applied inconsistently

### Milestones

```
Milestone: 1.0.0 — Core Monitoring
Goal: Bot reliably monitors configured groups for keywords and sends alerts
Due: 2026-04-15
Issues: TMB-1 through TMB-5
```

**Rules:**
- One goal per milestone, expressed as a user-facing outcome
- Set a due date and honour it (move issues out rather than moving the date)
- Every open issue has a milestone or is in "Backlog"
- Review milestone scope at the start; don't add mid-sprint

### Estimates

For a small solo team, T-shirt sizing is simpler than story points:

| Size | Meaning |
|------|---------|
| S | Half a day or less |
| M | 1–2 days |
| L | 3–5 days |
| XL | Needs splitting |

Rules:
- Estimate before starting, not after
- If actual time is consistently 2× the estimate, the issue was too vague
- Never estimate bugs until root-caused
- Never estimate to create pressure; estimate to detect scope problems early

---

## 5. GitLab-Specific Practices

### Issue Templates

Store at `.gitlab/issue_templates/<name>.md`. Quick actions (`/label`, `/milestone`) auto-apply metadata on creation.

**Feature template:**
```markdown
## Context
<!-- Why does this exist? Link parent epic if applicable. -->

## What to build
<!-- Precise description. For handler changes: trigger condition, filter, alert format. -->

## Acceptance criteria
- [ ] Given ..., when ..., then ...
- [ ] Error cases: ...
- [ ] Tests: ...

## Out of scope
<!-- Explicitly list what this issue does NOT cover. -->

## Implementation notes
<!-- Optional: files to touch, gotchas, constraints. -->

/label ~feature
/milestone %"Current Sprint"
```

**Bug template:**
```markdown
## Steps to reproduce
1. ...
2. ...

## Expected behaviour

## Actual behaviour

## Environment
<!-- Local / staging / production. Version / commit. -->

## Logs / screenshots

/label ~bug ~priority::high
```

### Scoped Labels

Use `::` to create mutually exclusive label groups. GitLab prevents applying two labels from the same scope simultaneously (e.g., `priority::high` and `priority::low`).

### Board Configuration

For a solo/small team, simple Kanban:
```
Open → In Progress → In Review → Done
```

Constrain WIP: max 2 issues "In Progress". More is a sign of blocking, not multitasking.

### Commit and MR Conventions

Include `Closes #<iid>` in commit messages or MR descriptions — GitLab auto-closes the issue when the MR is merged:

```
TMB-2 Bot detects photo captions containing keywords

- Add filters.photo handler with caption keyword check
- Extend send_alert to handle caption text
- Update CLAUDE.md with new handler documentation

Closes #2
```

MR title should mirror the issue title. This keeps the git log readable without opening GitLab.

### Epics (Premium+)

Use epics for features that span 2+ milestones:

```
Epic: Advanced Monitoring
  - Milestone 1.0.0: TMB-1 text monitoring, TMB-2 photo captions, TMB-3 deduplication
  - Milestone 1.1.0: TMB-6 forwarded messages, TMB-7 alert formatting options
```

Epic description should contain:
- The business goal (one sentence)
- A link to any external spec or design doc
- Known constraints or non-goals
- Child issue checklist (auto-populated once issues are associated)

### Iteration Cadence

- **Weekly:** Groom top of backlog, ensure top 5 issues are `status::ready`
- **Per-issue:** Write AC before coding; update with discoveries during implementation; close with a comment summarising what was done and any deferred follow-up issues

---

## 6. Good vs Bad Examples

### Issue Titles

| Bad | Good |
|-----|------|
| Fix alerts | `[Bug] Bot sends duplicate alerts when keyword appears in edited message` |
| Add monitoring | `Bot detects keywords in photo captions and sends alerts` |
| Update config | `Bot supports per-group keyword lists via GROUP_KEYWORDS .env variable` |
| Refactor code | `send_alert uses message link instead of plain group title when available` |
| Fix bot | `[Bug] Bot crashes when monitored group has no title` |

### Acceptance Criteria

| Bad | Good |
|-----|------|
| "It works" | "Alert is sent to TARGET_USER within 5s when keyword appears in a monitored group" |
| "Errors are handled" | "Bot logs warning and continues when send_message fails for one alert" |
| "Tests pass" | "pytest covers: keyword match, no match, case-insensitive match, anonymous sender" |
| "Performance is good" | "Bot processes 100 messages/second without missing keyword matches" |

### Epic Decomposition

| Horizontal (bad) | Vertical (good) |
|-----------------|----------------|
| Issue: "Config parsing for new feature" | Issue: "Bot monitors photo captions for keywords and sends alerts" |
| Issue: "New Pyrogram filter" | Issue: "Bot monitors forwarded messages for keywords" |
| Issue: "Handler function" | Issue: "Alert includes direct link to original message" |
| Issue: "Alert formatting" | Issue: "Bot deduplicates alerts for edited messages" |

---

## Issue Readiness Checklist

Before marking an issue ready to work on:

- [ ] Title states the outcome, not the implementation
- [ ] Context explains why this exists
- [ ] AC are specific enough to write tests from
- [ ] AC cover at least one error case
- [ ] Out-of-scope items are listed
- [ ] Issue satisfies INVEST
- [ ] Dependencies are noted in the description
- [ ] Labels applied: type
- [ ] Milestone assigned
