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
| [blog-post-writer](./skills/blog-post-writer/SKILL.md) | `/oz-skills:blog-post-writer` | Turns a project, hack, opinion, or reflection into a published post for posts.oztamir.com in Oz's voice. Interviews you first to get the real story (the itch, the dead-ends, the payoff), then drafts section-by-section and emits a Ghost-ready Markdown file. Bundles real posts as style exemplars. |
| [humanizer](./skills/humanizer/SKILL.md) | `/oz-skills:humanizer` | Removes signs of AI-generated writing from text — inflated symbolism, promotional language, em dash overuse, rule of three, AI vocabulary, filler phrases, and more. Vendored from [blader/humanizer](https://github.com/blader/humanizer) and auto-synced. |
| [import-skill](./skills/import-skill/SKILL.md) | `/oz-skills:import-skill` | Meta-skill: vendor an external skill from a linked GitHub repo into this plugin. Copies it into `skills/`, registers it in `.github/vendored-skills.json` so the shared workflow auto-syncs it from upstream weekly, adds attribution, bumps the version, and updates this table. |
| [prompt-optimizer](./skills/prompt-optimizer/SKILL.md) | `/oz-skills:prompt-optimizer` | Turns a rough prompt into a strong, model-specific one engineered to the official prompting guide for the target model (GPT-5.5, Claude Opus 4.8, Claude Fable 5, …). Never assumes your intent — interviews you with AskUserQuestion first, then hands back a copy-ready prompt to paste into a fresh session. Designed to run on the first message of a session. |
| [stop-slop](./skills/stop-slop/SKILL.md) | `/oz-skills:stop-slop` | Removes predictable AI writing patterns from prose — filler phrases, formulaic structures, passive voice, em dashes, vague declaratives — and scores drafts across directness, rhythm, trust, authenticity, and density. Vendored from [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) and auto-synced. |
| [unvibe](./skills/unvibe/SKILL.md) | `/oz-skills:unvibe` | Reworks a vibe-coded PR into production code a reviewer will trust. Runs five read-only reasoning passes (study the pre-change code and its conventions, understand the PR, map where it doesn't fit, hunt over-engineering) before any edit, then synthesizes a plan and applies it as minimal, idiomatic, atomic commits — ending with a change summary and an optional reviewer guide. Language-agnostic. |
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
