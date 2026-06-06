# oz-skills

Oz Tamir's personal collection of [Claude Code](https://code.claude.com) skills,
packaged as an installable plugin.

Skills teach Claude Code how to do specific things well — Claude loads a skill
automatically when its description matches what you're working on, or you can
invoke one explicitly with `/oz-skills:<skill-name>`.

## Install

This repo is both a Claude Code **plugin** and a single-plugin **marketplace**,
so installing is two commands inside Claude Code:

```
/plugin marketplace add OzTamir/skills
/plugin install oz-skills@oztamir
```

To update later:

```
/plugin marketplace update oztamir
```

CLI equivalents (non-interactive):

```bash
claude plugin marketplace add OzTamir/skills
```

## What's inside

Each skill lives in its own folder under `skills/` and is auto-discovered:

```
skills/
└── <skill-name>/
    └── SKILL.md        # required: the skill itself
    └── ...             # optional supporting files (scripts, templates, refs)
```

<!-- skills-list:start -->
| Skill | Invoke | What it does |
| --- | --- | --- |
| [full-deliberate-mode](./skills/full-deliberate-mode/SKILL.md) | `/oz-skills:full-deliberate-mode` | When you say you're in "Full Deliberate Mode" / "FDM", Claude stops ghostwriting and instead helps you structure your thinking — using questions to find a structure you like, then prompting you to fill it with your own exact words. Never puts words in your mouth. |
<!-- skills-list:end -->

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md`.
2. Give it YAML frontmatter with a sharp `description` — Claude uses this to
   decide when to auto-invoke the skill, so describe **what it does and when to
   use it**:

   ```markdown
   ---
   name: my-skill
   description: Use when <situation> to <do the thing>. Triggers on <keywords>.
   ---

   # My Skill

   Step-by-step instructions for Claude to follow…
   ```

3. Keep the skill name in kebab-case; the folder name is the skill name and
   becomes `/oz-skills:<skill-name>`.
4. Bump `version` in `.claude-plugin/plugin.json` (and the matching entry in
   `.claude-plugin/marketplace.json`) so installed users get the update.

For deeper guidance on authoring skills, use the `superpowers:writing-skills`
or `skill-creator` skill while working in this repo. See also
[AGENTS.md](./AGENTS.md) for conventions.

## Repo layout

```
.
├── .claude-plugin/
│   ├── plugin.json         # plugin manifest
│   └── marketplace.json    # marketplace catalog (source ".")
├── skills/                 # the skills (auto-discovered)
├── AGENTS.md               # conventions for agents working in this repo
├── CLAUDE.md -> AGENTS.md  # symlink so Claude Code reads the same guidance
├── README.md
└── LICENSE
```

## License

[MIT](./LICENSE) © Oz Tamir
