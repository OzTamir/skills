---
name: import-skill
description: >-
  Use when the user links or pastes a GitHub repo/URL for an external Claude
  skill and wants it added, imported, vendored, or pulled into THIS oz-skills
  plugin repo. Triggers on "add this skill", "import this skill from <github
  link>", "vendor this skill", "pull this skill repo in", or pasting a
  github.com link alongside any intent to include it here. Replicates the
  standard vendoring workflow: copy the skill into skills/<name>/, register it in
  .github/vendored-skills.json so the shared sync-vendored-skills workflow keeps
  it current automatically, add MIT-compatible attribution, bump the plugin
  version, and update the README. Use this even if the user never says the word
  "vendor" — any "add this external skill to the repo" request qualifies.
---

# Import Skill

Vendor an external skill from a GitHub repo into this plugin, wired up so it
**stays in sync with upstream automatically**. The hard-won design decisions are
already baked into the repo's tooling — your job is to follow the workflow, not
reinvent it.

## Why it works this way (read before deviating)

- **Vendored, not submoduled.** Claude Code's plugin installer does a plain
  `git clone` without `--recurse-submodules`, so a submodule would land as an
  *empty* folder for anyone installing the published marketplace. We copy the
  files in instead.
- **One workflow for all imports.** Every vendored skill is a row in
  `.github/vendored-skills.json`. The single `sync-vendored-skills` workflow
  reads that manifest and refreshes them all weekly. Importing a skill means
  **adding a manifest row**, never adding a new workflow.
- **Attribution lives outside the synced set.** `LICENSE` and `README.md` inside
  the skill folder are *not* listed in the manifest, so the auto-sync never
  overwrites them. Only the declared `paths` (normally just `SKILL.md`) get
  refreshed.

## Workflow

### 1. Inspect the upstream repo

Shallow-clone it to a temp dir and find the skill:

```bash
cd /tmp && rm -rf import-inspect && git clone --depth 1 <repo-url> import-inspect
find import-inspect -name SKILL.md -not -path '*/.git/*'
```

Determine, from the `SKILL.md` you find:

- **`name`** — read the `name:` field in the frontmatter (kebab-case). This
  becomes the folder `skills/<name>/` and the invocation `/oz-skills:<name>`.
- **`upstream_dir`** — the directory *containing* `SKILL.md` relative to the repo
  root. `.` if it's at the root; otherwise e.g. `skills/foo`.
- **`paths`** — the files that make up the skill. Usually just `["SKILL.md"]`.
  If the `SKILL.md` references supporting files by relative path (scripts,
  templates, `references/*`), `grep` for them and include each one so the sync
  pulls them too.
- **`ref`** — the branch to track. Default `main`; ask only if the repo's default
  branch is clearly something else or the user wants a pinned tag/sha.

### 2. Check the license

Read the upstream `LICENSE`. This repo is **MIT**, so MIT / BSD / Apache-2.0 /
public-domain upstreams vendor cleanly with attribution. If the license is
**absent, copyleft (GPL/AGPL), or otherwise incompatible**, stop and surface it
to the user before copying anything — don't silently vendor it.

### 3. Branch

New skill = a feature. If on `main`, branch first (Conventional Commits):

```bash
git checkout -b feat/<name>-skill
```

### 4. Register it in the manifest

Add an entry to `.github/vendored-skills.json` under `skills`:

```json
{
  "name": "<name>",
  "repo": "<owner>/<repo>",
  "ref": "main",
  "upstream_dir": ".",
  "paths": ["SKILL.md"]
}
```

### 5. Pull the files in

Run the shared sync script in local mode (no `--commit`) — it reads the manifest,
fetches each declared path into `skills/<name>/`, and validates that any
`SKILL.md` has real frontmatter:

```bash
bash .github/scripts/sync-vendored-skills.sh
```

This is the *same* code path the weekly workflow uses, so if it succeeds here the
auto-sync will too.

### 6. Add attribution

These files are intentionally outside the manifest so auto-sync won't touch them:

```bash
cp /tmp/import-inspect/<upstream_dir>/LICENSE skills/<name>/LICENSE   # if present
```

Write `skills/<name>/README.md` noting the skill is vendored, linking the
upstream repo, and warning not to hand-edit `SKILL.md` (auto-sync overwrites it).
Mirror the style of `skills/humanizer/README.md`.

### 7. Bump the plugin version (minor — new skill)

A new skill is a *minor* bump. Edit **both** files, keeping them in sync:

- `.claude-plugin/plugin.json` → `version`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

(The auto-sync workflow handles *patch* bumps later when an already-vendored
skill's content changes upstream. You only do the minor bump for the new addition.)

### 8. Update the README skills table

Add a row between the `<!-- skills-list:start -->` / `:end` markers in
`README.md`, matching the existing format. Note in the "What it does" cell that
it's vendored from upstream and auto-synced.

### 9. Validate

```bash
python3 -m json.tool .claude-plugin/plugin.json > /dev/null
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
python3 -m json.tool .github/vendored-skills.json > /dev/null
head -1 skills/<name>/SKILL.md   # should be '---'
```

### 10. Report

Summarize what changed and the new version. **Commit/PR only if the user asks**
(repo convention: Conventional Commits, e.g. `feat: vendor <name> skill`). Note
that the GitHub Action needs **Actions write permission** (Settings → Actions →
General → "Read and write permissions") for the auto-sync to push.

## What the auto-sync gives them

Once merged, `sync-vendored-skills` runs every Monday (and on manual dispatch),
refreshes every manifested skill from upstream, and — only if something actually
changed — bumps the patch version and commits to `main`. The user never re-copies
a file by hand.
