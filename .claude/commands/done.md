---
description: Commit work-in-progress, push the branch, and open or update a PR. Run before ending a session on this shared repo.
---

You are closing out a working session on a shared repository. Your job is to make sure no work is lost and the team can see what's been done. Do NOT merge the PR — that's the owner's call.

## Step 1: Check the branch

Run `git branch --show-current` and `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` to get the current and default branches.

- **If on the default branch (`main`/`master`)**: STOP. Tell the user: "You're on the default branch — work on shared repos belongs on a feature branch. Want me to create one for what we worked on?" Do not commit on the default branch.
- **If on a feature branch**: continue.

## Step 2: Check what's changed

Run `git status` to see modified and untracked files.

- If nothing is modified or staged, skip to Step 5 — you may still need to open/update a PR for previously committed work.
- If there are changes, look back at the conversation and write **one short paragraph** describing what got done this session. This goes in the commit message and PR body. Pull from the actual work — don't invent or pad.

## Step 3: Stage and commit

Stage tracked changes with `git add -u`. For untracked files, ask the user before adding (they may be local-only experiments or accidentally-created files).

Commit with an imperative subject and 1-2 sentences of body from the session intent:

```bash
git commit -m "$(cat <<'EOF'
<imperative subject>

<one-paragraph session intent>

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Step 4: Push the branch

```bash
git push -u origin <branch>
```

If the push is rejected (remote has new commits on this branch), pull with rebase and retry. Flag conflicts to the user — never auto-resolve.

## Step 5: Open or update the PR

Check for an existing PR with `gh pr view`.

- **No PR**: open one against the default branch with `gh pr create`. Title = commit subject. Body should include:
  - One-paragraph summary of what changed
  - Why (the session intent)
  - Reviewer checklist: `- [ ] Diff makes sense`, `- [ ] No secrets/data committed`, `- [ ] Doesn't break the live deployment`
- **PR exists**: post a comment with the latest session note so the running context is visible to reviewers.

## Step 6: Stop. Don't merge.

Print a closing summary:

```
Session committed and pushed.
- Branch: <branch>
- Commit: <hash> — <subject>
- PR: <url> (status: open / draft)
- Next: owner reviews and merges.
```

Do NOT run `gh pr merge`. That's the owner's decision after reviewing the diff. The owner is named in `.github/CODEOWNERS` and `CONTRIBUTING.md`.

## Guidelines

- If there's nothing to commit and no PR to update, say so in one sentence and exit. Don't fabricate session content.
- Don't add files the user didn't intend to commit. When in doubt, ask before staging.
- Never force-push, never skip hooks, never commit secrets.
- If the PR already exists and has unresolved review comments, mention them in the summary so the user knows there's pending feedback.
