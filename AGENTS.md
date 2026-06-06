# AGENTS.md

Guidance for AI agents (and humans) working in this repo.

## What this repo is

`oz-skills` is a Claude Code **plugin** that bundles personal skills, and is
also published as a single-plugin **marketplace** so it can be installed with
`/plugin marketplace add OzTamir/skills`. The repo root *is* the plugin.

```
.claude-plugin/plugin.json       # plugin manifest — name, version, author
.claude-plugin/marketplace.json  # marketplace catalog; the one plugin has source "."
skills/<name>/SKILL.md           # one folder per skill, auto-discovered
```

## Authoring skills

- One skill = one folder `skills/<skill-name>/` containing `SKILL.md`.
- Folder name is the skill name (kebab-case). It becomes `/oz-skills:<skill-name>`.
- `SKILL.md` must start with YAML frontmatter. The most important field is
  `description`: write **what the skill does and when to use it**, because
  Claude matches against this to auto-invoke. Lead with "Use when …".
- Put supporting files (scripts, templates, reference docs) alongside `SKILL.md`
  and reference them by relative path from within the skill.
- Prefer the `superpowers:writing-skills` or `skill-creator` skill when creating
  or editing a skill — they encode the current best practices and can run evals.

Minimal skill:

```markdown
---
name: example-skill
description: Use when <situation> to <outcome>. Triggers on <keywords>.
---

# Example Skill

Instructions for Claude…
```

## Conventions

- **Kebab-case** for skill folder names and the `name` frontmatter field.
- Keep `description` tight and trigger-oriented; it's the single biggest lever
  on whether the skill fires at the right time.
- Skills should be self-contained — no assumptions about the user's repo layout
  unless the skill is explicitly about a specific stack.

## Versioning & releasing

When you add or meaningfully change a skill:

1. Bump `version` in **both** `.claude-plugin/plugin.json` and the matching
   plugin entry in `.claude-plugin/marketplace.json` (keep them in sync).
2. Use semver: patch for fixes, minor for new skills, major for breaking changes.
3. Commit with [Conventional Commits](https://www.conventionalcommits.org)
   (`feat:`, `fix:`, `docs:`, `chore:` …).
4. Keep the skills list in `README.md` (between the `skills-list` markers) up to
   date when adding/removing a skill.

## Validating changes

JSON manifests must stay valid (a malformed manifest breaks install):

```bash
python3 -m json.tool .claude-plugin/plugin.json > /dev/null
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
```

To smoke-test locally before pushing, add this repo as a local marketplace in
Claude Code:

```
/plugin marketplace add /Users/oztamir/Code/oz-skills
/plugin install oz-skills@oztamir
```

## Notes

- `CLAUDE.md` is a symlink to this file — edit `AGENTS.md`, not the symlink.
- `.claude/settings.local.json` and `tmp/` are gitignored (machine-local).
