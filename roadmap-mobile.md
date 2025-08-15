## Roadmap: Mobile → Agent → Private Git Branch Workflow

### Goals
- **Mobile-first control**: Trigger coding tasks from a phone with minimal friction.
- **Safety**: No direct repo write from the phone; all changes go through a bot on a branch + PR with checks.
- **Observability**: Every task produces a branch, a PR, and CI results you can review on GitHub mobile.
- **Replaceable agent**: Start simple; later swap in Cursor Agent or another agent without changing the outer workflow.

### High-level Architecture
1. **Mobile interface** (choose 1 to start):
   - **GitHub Issue/PR comments** using slash commands (recommended Phase 1): type `/run <task>` from GitHub mobile.
   - Slack/Discord/Telegram bot → webhook → agent (Phase 2).
2. **Orchestrator**: GitHub Actions job (or a small server) receives the task, validates it, and runs the agent.
3. **Agent**: Makes local edits, runs format/lint/tests, then commits to a new branch like `mobile/<timestamp>-<slug>`.
4. **Output**: Open a PR to `main` with a summary comment and CI checks.

## Recommended Phase 1: Use GitHub comments as the mobile UI
- **Why**: Works entirely in GitHub (native mobile app), minimal new infra, tight permissions.
- **How it feels**: From your phone, comment `/run add an endpoint that returns build info` on an issue. A workflow branches, edits, opens a PR, and posts status.

### Git repository and settings changes
- **Branch model**:
  - Feature branches per task: `mobile/YYYYMMDD-HHMM-<slug>`.
  - `main` stays protected; enforce PR-only merges.
- **Protected branch rules** (in repo settings):
  - Require PR reviews (e.g., 1 approval, or only your approval).
  - Require status checks to pass: CI (test/lint/typecheck) and optional security scan.
  - Restrict who can push to `main` (bot excluded), allow merges via PR only.
- **Commit conventions**:
  - Conventional commits, e.g., `feat(mobile): <task summary> (#<issue>)`.
  - Configure a bot identity (name/email); optionally require signed commits.
- **PR conventions**:
  - PR template with sections: summary, risk, tests, screenshots, rollback.
  - Labels: `from-mobile`, `agent`, `needs-review`.

### Permissions and authentication
- **Use GitHub App or GITHUB_TOKEN**:
  - Start with workflow `GITHUB_TOKEN` (scoped to repo). Permissions: contents: write; pull-requests: write; issues: write.
  - Later: switch to a **GitHub App** with least-privilege permissions and branch allowlist.
- **Secrets handling**:
  - Store 3rd-party keys (LLM, telemetry) as repo/environment secrets; never expose to mobile UI.
  - Add a secret scan step in CI.

### CI/CD additions (Phase 1)
- **Workflow 1: mobile-agent**
  - Trigger: `issue_comment` with `/run <task>`.
  - Steps: checkout → derive branch → run agent → format/lint/tests → commit → push → open PR → comment link.
- **Workflow 2: pr-ci**
  - Trigger: `pull_request`.
  - Steps: install deps → lint → typecheck → tests → optional SAST and secret scan.
- **Branch protection** requires Workflow 2 to pass before merge.

### Agent implementation options
- **POC agent** (Day 1): deterministic script that applies a simple change so the end-to-end path is proven (creates file, updates docs, etc.).
- **LLM-based agent** (Phase 1b): run a repo-aware script (OpenAI/Anthropic/local) that edits files per task, then validates with tests.
- **Cursor Agent integration** (Phase 2): if/when a headless/CLI/API is available or via a persistent devbox, route tasks to Cursor Agent to propose edits, then commit via the bot.

### Mobile UX flow (Phase 1)
- From GitHub mobile:
  - Comment `/run <task>` on an Issue.
  - Bot replies with: branch name, PR link, and CI status.
  - Review diff and checks; optionally comment `/approve` to auto-merge (optional follow-up workflow), or merge manually.

### Guardrails and safety
- **Allowlist edits**: Agent only writes under configured paths (e.g., `src/`, `docs/`).
- **Diff size caps**: Fail if changes exceed thresholds unless `/force` is present.
- **Tests first**: Run tests before and after edits; block PR if failing.
- **Secret scanning**: Fail if secrets are detected in diff.
- **Rate limits**: Limit concurrent runs and total runs/day.

### Rollout plan
- **Phase 0 (1–2 hrs)**
  - Enable branch protection on `main`.
  - Add PR template and labels.
- **Phase 1 (half-day)**
  - Add `mobile-agent` workflow (below) using the POC agent step.
  - Add `pr-ci` workflow skeleton to run tests.
  - Dry-run on a sandbox repo.
- **Phase 1b (1–2 days)**
  - Swap POC step for LLM agent with repo context, format/lint/tests.
  - Add `/dry-run` command to open a PR with changes but mark as draft.
- **Phase 2 (optional)**
  - Integrate a chat bot (Telegram/Slack) or Cursor Agent.
  - Add `/approve` and `/revert` command workflows.

### Success criteria
- From phone → comment → PR with passing checks in under 5 minutes.
- ≥90% of agent PRs require ≤1 manual edit before merge.
- No direct writes to `main`; audit trail present on every change.

## Appendix A: Example Workflow – mobile-agent (POC)
Use this now; replace the "Example agent change" step with your agent later.

```yaml
name: Mobile Agent (POC)

on:
  issue_comment:
    types: [created]

permissions:
  contents: write
  pull-requests: write
  issues: write
  checks: read
  actions: read

jobs:
  run:
    if: contains(github.event.comment.body, '/run ')
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Derive task and branch
        id: meta
        run: |
          slug=$(echo "${{ github.event.comment.body }}" | sed -E 's/^.*\/run[[:space:]]+//' | tr ' ' '-' | tr -cd '[:alnum:]-' | cut -c1-60)
          ts=$(date -u +'%Y%m%d-%H%M%S')
          echo "branch=mobile/$ts-$slug" >> $GITHUB_OUTPUT
          echo "task=${{ github.event.comment.body }}" >> $GITHUB_OUTPUT

      - name: Create work branch
        run: |
          git switch -c "${{ steps.meta.outputs.branch }}"

      - name: Example agent change (POC)
        run: |
          printf "Requested via mobile:\n\n%s\n" "${{ steps.meta.outputs.task }}" > MOBILE_AGENT_PROOF.md

      - name: Format/lint (optional)
        run: echo "run your formatter/linter here"

      - name: Commit and push
        run: |
          git config user.name "mobile-agent-bot"
          git config user.email "actions@users.noreply.github.com"
          git add -A
          git commit -m "feat(mobile): ${{ steps.meta.outputs.task }}"
          git push --set-upstream origin "${{ steps.meta.outputs.branch }}"

      - name: Open PR
        uses: peter-evans/create-pull-request@v6
        with:
          branch: ${{ steps.meta.outputs.branch }}
          title: "Mobile agent: ${{ steps.meta.outputs.task }}"
          body: |
            Created by mobile agent from [comment](${{ github.event.comment.html_url }}).
            - Branch: `${{ steps.meta.outputs.branch }}`
```

## Appendix B: Example Workflow – pr-ci (skeleton)
Require this workflow to pass in branch protection.

```yaml
name: PR CI

on:
  pull_request:
    branches: [ main ]

permissions:
  contents: read
  checks: write

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # - uses: actions/setup-node@v4
      #   with:
      #     node-version: '20'
      # - run: npm ci
      # - run: npm run lint
      # - run: npm test -- --ci
      - run: echo "replace with your real steps"
```

## Appendix C: Optional follow-ups
- **/approve** workflow to auto-merge if checks pass and author is allowed.
- **/dry-run** to open a draft PR.
- **Ephemeral preview** (Vercel/Netlify/Render) per PR for quick mobile viewing.
- **CODEOWNERS** to require your approval on risky paths.
- **Conventional commits + changesets** for automatic versioning.