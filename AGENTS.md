# BreakOut project instructions

Follow `/Users/ermagent/.codex/AGENTS.md` and the user's current instructions.
The global file is the source of truth for shared engineering, authorization,
verification, cost discipline, and delivery rules. Keep this file focused on
BreakOut-specific guidance rather than copying the global rules.

## Review scope

Use the shared review policy. Material changes to risk gates, immutable evidence, or transactional state count as consequential risks for high review.

## Research and operation

For this project's research and operation, read `skills/breakout-research/SKILL.md`.

Current scope is public-data research and paper simulation only. The project has no
private exchange client, account credentials, purchase operation, or live order path.
Do not substitute a Kraken exchange account for the user's intended Breakout account.
Preserve recorded runs and frozen source/configuration snapshots. A changed strategy,
cost assumption, gate, or implementation creates a new version; never rewrite earlier
intents or retrospectively label an exploratory result as an untouched holdout.

## Git authorization

The user authorized automatic commits and pushes on 2026-09-08. After completing
and appropriately verifying requested work, commit the task's changes and push to
`origin` (`https://github.com/narupu3-wq/breakout.git`) without asking again.
Preserve unrelated work and inspect outgoing changes for secrets and unintended
files. This authorization does not include force pushes, remote history rewrites,
merges, deployment, or publication outside this repository.
