---
name: gitlab
description: Use when starting, finishing, or checking the status of a GitLab issue in this project — reading issue details, moving issues through the workflow (Todo → In Progress → In Review → Done), or updating issue state after completing work.
---

# GitLab Issue Management

## Project Config

| Key | Value |
|-----|-------|
| Base URL | `https://gitlab.kidsgames.top/api/v4/projects/6` |
| Auth | `?private_token=<TOKEN>` or header `PRIVATE-TOKEN: <TOKEN>` |
| Token | User provides per session — never stored |

## Workflow

Labels drive issue state. Issues move through:

```
Todo  →  In Progress  →  In Review  →  Done
```

Label IDs are not required — use label names directly in API calls.

## Creating a New Issue

Before creating an issue, always ask the user for:

1. **Type** — bug or feature? (sets label: `bug` or `feature`)
2. **Milestone** — which milestone to assign it to?

**Never add the `Todo` label when creating an issue.** Only `bug` or `feature`.

```bash
curl -s -X POST "https://gitlab.kidsgames.top/api/v4/projects/6/issues" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<title>",
    "description": "<description>",
    "labels": "<bug|feature>",
    "milestone_id": <id>
  }'
```

To find milestone IDs:
```bash
curl -s "https://gitlab.kidsgames.top/api/v4/projects/6/milestones?private_token=<TOKEN>"
```

## Common Operations

### Get issue details
```
GET /issues/:iid
```

### List open issues
```
GET /issues?state=opened&per_page=20&order_by=iid&sort=asc
```

### Move issue to In Progress (when starting work)
```
PUT /issues/:iid
Body: { "add_labels": "In Progress", "remove_labels": "Todo" }
```

### Move issue to In Review (when implementation is complete)
```
PUT /issues/:iid
Body: { "add_labels": "In Review", "remove_labels": "In Progress" }
```

### Close issue and mark Done (after review passes)
```
PUT /issues/:iid
Body: { "state_event": "close", "add_labels": "Done", "remove_labels": "In Review" }
```

### Add a comment
```
POST /issues/:iid/notes
Body: { "body": "comment text" }
```

## WebFetch Usage

Use the `WebFetch` tool with GET requests (read-only). For PUT/POST (mutations), use `Bash` with `curl`:

```bash
# Move issue to In Progress
curl -s -X PUT "https://gitlab.kidsgames.top/api/v4/projects/6/issues/2" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"add_labels":"In Progress","remove_labels":"Todo"}'

# Move to In Review
curl -s -X PUT "https://gitlab.kidsgames.top/api/v4/projects/6/issues/2" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"add_labels":"In Review","remove_labels":"In Progress"}'

# Close issue as Done (after review)
curl -s -X PUT "https://gitlab.kidsgames.top/api/v4/projects/6/issues/2" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"state_event":"close","add_labels":"Done","remove_labels":"In Review"}'
```

## Starting Work on an Issue

When starting work, do **all three steps immediately** — before planning or writing any code:

**1. Fetch issue details**
```bash
# via WebFetch
GET /issues/:iid
```

**2. Move to In Progress**
```bash
curl -s -X PUT "https://gitlab.kidsgames.top/api/v4/projects/6/issues/:iid" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"add_labels":"In Progress","remove_labels":"Todo"}'
```

**3. Find and check out the branch locally**

GitLab auto-creates a branch from the issue title when the issue is created. Branch name follows `{iid}-kebab-issue-title`. Find it and check out locally:

```bash
# List remote branches to find the auto-created one
git fetch origin
git branch -r | grep "^  origin/{iid}-"

# Checkout
git checkout -b <branch-name> origin/<branch-name>
```

If no auto-created branch exists, create one manually then check it out:
```bash
curl -s -X POST "https://gitlab.kidsgames.top/api/v4/projects/6/repository/branches" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"branch":"{iid}-short-description","ref":"develop"}'

git fetch origin
git checkout -b {iid}-short-description origin/{iid}-short-description
```

**Only after these three steps are complete, proceed to planning (feature-spec skill).**

## Finishing Work on an Issue

When implementation is complete, committed, and pushed:

**1. Create a Merge Request targeting `develop`**

Include `Closes #N` in the MR description — GitLab will auto-close the issue when the MR is merged.

```bash
curl -s -X POST "https://gitlab.kidsgames.top/api/v4/projects/6/merge_requests" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d "{
    \"source_branch\": \"<branch-name>\",
    \"target_branch\": \"develop\",
    \"title\": \"TMB-{iid} <short description>\",
    \"description\": \"## What was done\n\n<bullet list summarizing the changes made>\n\nCloses #{iid}\",
    \"should_remove_source_branch\": true
  }"
```

**2. Move issue to In Review**
```bash
curl -s -X PUT "https://gitlab.kidsgames.top/api/v4/projects/6/issues/:iid" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"add_labels":"In Review","remove_labels":"In Progress"}'
```

After the user reviews and merges the MR, GitLab auto-closes the issue. Then mark Done:

**3. Mark Done (after MR merged)**
```bash
curl -s -X PUT "https://gitlab.kidsgames.top/api/v4/projects/6/issues/:iid" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"add_labels":"Done","remove_labels":"In Review"}'
```

## Accepting an MR

When the user says "accept MR" or "merge MR":

**1. Merge the MR (deletes remote branch automatically)**
```bash
curl -s -X PUT "https://gitlab.kidsgames.top/api/v4/projects/6/merge_requests/:mr_iid/merge" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"should_remove_source_branch": true}'
```

**2. Switch to `develop` and pull**
```bash
git checkout develop && git pull
```

**3. Mark issue Done** (if issue not already auto-closed by `Closes #N` in MR description)
```bash
curl -s -X PUT "https://gitlab.kidsgames.top/api/v4/projects/6/issues/:iid" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"add_labels":"Done","remove_labels":"In Review"}'
```
> If the MR description contained `Closes #N`, GitLab auto-closes the issue on merge — skip the issue update.

---

## Reordering Issues on a Board

Use `PUT /projects/6/issues/:iid/reorder` with `move_after_id` (the global issue ID to place this issue after).

**Board display:** GitLab shows issues with the highest position at the **top**. So to get issue A above issue B, move A after B.

```bash
# Place #3 above #4 on the board (3 appears on top)
curl -s -X PUT "https://gitlab.kidsgames.top/api/v4/projects/6/issues/3/reorder" \
  -H "PRIVATE-TOKEN: <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"move_after_id": 4}'
```

**To reorder a full sequence (top → bottom: A, B, C, D):**
Build the chain from the bottom up — move each issue after the one below it:
```bash
# Desired top→bottom: A, B, C, D
# Move C after D, then B after C, then A after B
move C after D  →  move B after C  →  move A after B
```

**Note:** `move_after_id` uses the global issue `id`, not `iid`. In this project they happen to be equal (id == iid).

## Other Rules

- **iid** = issue number in the project (e.g., TMB-2 = iid 2)
- Base branch for new branches: `develop`
