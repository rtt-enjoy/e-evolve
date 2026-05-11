# Commit Workflow

Every prompt that changes repository files must end with a commit and push after
the requested work has been verified.

## Prompt Change Flow

1. Read `CLAUDE.md` before taking action.
2. Make the smallest scoped change that satisfies the prompt.
3. Run the most relevant verification for the changed files.
4. Check `git status --short`.
5. If files changed, create one commit with a commitlint-compatible Conventional
   Commit message.
6. Push the current branch to `origin`.

If the worktree is clean after verification, skip the commit.

## Commit Message Rules

Prompt-driven commits use this header shape:

```text
<type>(<scope>): <subject>
```

The scope is optional:

```text
<type>: <subject>
```

Use lower-case types from commitlint's default set:

```text
build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test
```

Keep the header at 72 characters or less. The subject must be non-empty and must
not end with a period.

Good examples:

```text
docs: document prompt commit workflow
fix(earning): handle empty article topics
test(commands): cover issue command parsing
```

Avoid emoji or custom prefixes for prompt-driven commits. Bot-generated cycle
commits may keep their existing operational format when produced by the bot.
