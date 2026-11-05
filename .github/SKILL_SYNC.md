# Skill sync

The daily sync imports skills from PostHog and context-mill releases.

PR creation and auto-merge use the `releaser-ai-plugin` GitHub App.

GitHub Actions supplies the approval using `GITHUB_TOKEN`.

## Repository setup

An administrator must configure these settings before enabling auto-approval:

1. Open **Settings → Actions → General → Workflow permissions**.
2. Enable **Allow GitHub Actions to create and approve pull requests**.
3. Require the `tests` status check from GitHub Actions on `main`.

Organization policy must permit Actions approvals. Keep existing protections.

## Verification

After merging the workflow change, observe the next sync:

1. The release app creates the PR.
2. GitHub Actions approves it.
3. Auto-merge waits for required checks to pass before merging.

An approval failure stops the workflow before auto-merge is enabled.
