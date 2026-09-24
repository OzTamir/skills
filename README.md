# oz-skills

Oz Tamir's personal collection of [Claude Code](https://code.claude.com) skills,
packaged as an installable plugin.

Skills teach Claude Code how to do specific things well — Claude loads a skill
automatically when its description matches what you're working on, or you can
invoke one explicitly with `/oz-skills:<skill-name>`.

## Install

### As a Claude Code plugin (recommended)

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

CLI equivalent (non-interactive):

```bash
claude plugin marketplace add OzTamir/skills
```

### With the skills.sh CLI (any agent)

These skills are also installable with the [skills.sh](https://www.skills.sh)
CLI, which works with Claude Code, Cursor, Copilot, Windsurf, and other agents.
It copies the skill folders into your agent's skills directory:

```bash
# all skills in this repo, into the current project
npx skills add OzTamir/skills

# just the ones you want
npx skills add OzTamir/skills -s blog-post-writer -s prompt-optimizer

# install globally (user home) instead of per-project
npx skills add OzTamir/skills -g

# target specific agents
npx skills add OzTamir/skills -a claude-code -a cursor
```

Other useful commands: `npx skills list` to see what's installed,
`npx skills update` to pull the latest versions, `npx skills remove` to
uninstall.

Note that skills installed this way are **not** namespaced under the plugin, so
invoke them as `/<skill-name>` rather than `/oz-skills:<skill-name>`. Prefer the
plugin install on Claude Code — it tracks updates through the marketplace.

## What's inside

Each skill lives in its own folder under `skills/` and is auto-discovered:

```
skills/
└── <skill-name>/
    └── SKILL.md        # required: the skill itself
    └── ...             # optional supporting files (scripts, templates, refs)
```

<!-- skills-list:start -->
### Writing & editing

| Skill | Invoke | What it does |
| --- | --- | --- |
| [blog-post-writer](./skills/blog-post-writer/SKILL.md) | `/oz-skills:blog-post-writer` | Turns a project, hack, opinion, or reflection into a published post for posts.oztamir.com in Oz's voice. Interviews you first to get the real story (the itch, the dead-ends, the payoff), then drafts section-by-section and emits a Ghost-ready Markdown file. Bundles real posts as style exemplars. |
| [full-deliberate-mode](./skills/full-deliberate-mode/SKILL.md) | `/oz-skills:full-deliberate-mode` | When you say you're in "Full Deliberate Mode" / "FDM", Claude stops ghostwriting and instead helps you structure your thinking — using questions to find a structure you like, then prompting you to fill it with your own exact words. Never puts words in your mouth. |
| [humanizer](./skills/humanizer/SKILL.md) | `/oz-skills:humanizer` | Removes signs of AI-generated writing from text — inflated symbolism, promotional language, em dash overuse, rule of three, AI vocabulary, filler phrases, and more. Vendored from [blader/humanizer](https://github.com/blader/humanizer) and auto-synced. |
| [ogilvy-audit](./skills/ogilvy-audit/SKILL.md) | `/oz-skills:ogilvy-audit` | Audits a draft (memo, email, ad copy, article, landing page) against David Ogilvy's writing rules and the Roman & Raphaelson principles from *Writing That Works*, flagging violations by severity with quoted text and specific fixes. Imported from [@dickiebush](https://x.com/dickiebush/status/2062876058312224972) (no upstream repo; not auto-synced). |
| [plain-english](./skills/plain-english/SKILL.md) | `/oz-skills:plain-english` | Tightens prose in two passes — Orwell/Gowers plain-English rules (cut bloat, active voice, Saxon over Latinate, kill dying metaphors) then AI-detox (banned vocabulary, em-dash budget, no preamble/closer, no reflex rule-of-three). Runs as an audit or a rewrite. Vendored from [b1rdmania/claude-plain-english-skill](https://github.com/b1rdmania/claude-plain-english-skill) and auto-synced. |
| [simple-english](./skills/simple-english/SKILL.md) | `/oz-skills:simple-english` | Writes or rewrites technical text (docs, READMEs, runbooks, error messages, release notes) with the 53 rules of ASD-STE100 Simplified Technical English — 20/25-word sentence limits, one word one meaning, active voice, condition before command — so it's unambiguous and free of AI slop. Vendored from [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) and auto-synced. |
| [stop-slop](./skills/stop-slop/SKILL.md) | `/oz-skills:stop-slop` | Removes predictable AI writing patterns from prose — filler phrases, formulaic structures, passive voice, em dashes, vague declaratives — and scores drafts across directness, rhythm, trust, authenticity, and density. Vendored from [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) and auto-synced. |

### Prompting

| Skill | Invoke | What it does |
| --- | --- | --- |
| [prompt-optimizer](./skills/prompt-optimizer/SKILL.md) | `/oz-skills:prompt-optimizer` | Turns a rough prompt into a strong, model-specific one engineered to the official prompting guide for the target model (Claude Opus 5, Claude Fable 5, Claude Opus 4.8, GPT-5.6, GPT-5.5, …), including the Claude 5-generation context-engineering rules for system prompts, CLAUDE.md files, and skills. Never assumes your intent — interviews you with AskUserQuestion first, then hands back a copy-ready prompt to paste into a fresh session. Designed to run on the first message of a session. |

### Code

| Skill | Invoke | What it does |
| --- | --- | --- |
| [unvibe](./skills/unvibe/SKILL.md) | `/oz-skills:unvibe` | Reworks a vibe-coded PR into production code a reviewer will trust. Runs five read-only reasoning passes (study the pre-change code and its conventions, understand the PR, map where it doesn't fit, hunt over-engineering) before any edit, then synthesizes a plan and applies it as minimal, idiomatic, atomic commits — ending with a change summary and an optional reviewer guide. Language-agnostic. |

### Plugin tooling

| Skill | Invoke | What it does |
| --- | --- | --- |
| [import-skill](./skills/import-skill/SKILL.md) | `/oz-skills:import-skill` | Meta-skill: vendor an external skill from a linked GitHub repo into this plugin. Copies it into `skills/`, registers it in `.github/vendored-skills.json` so the shared workflow auto-syncs it from upstream weekly, adds attribution, bumps the version, and updates this table. |

### Tools & data

| Skill | Invoke | What it does |
| --- | --- | --- |
| [hebrew-rhymes](./skills/hebrew-rhymes/SKILL.md) | `/oz-skills:hebrew-rhymes` | Finds real Hebrew rhymes and wordplay through Dicta's [Charuzit](https://wordplay.dicta.org.il): rhymes, assonance/consonance (מצלול), alliteration, letter-and-nikud word patterns (תבנית מילה), and semantic-field search. Bundles a stdlib-only Python CLI for the site's unofficial API with every sidebar filter (part of speech, gender/number/person, tense, suffixes, syllable count, stress, loanwords, proper names, Tanakh). Handles vocalization of unpointed input. |
| [ikea-api](./skills/ikea-api/SKILL.md) | `/oz-skills:ikea-api` | Lets an agent search IKEA's live catalogue on its own — "find me a bookcase that fits a 70×30 cm alcove" — via IKEA's unofficial public APIs (documented in [idelsink/ikea-openapi](https://github.com/idelsink/ikea-openapi)). Bundles a stdlib-only Python CLI for text search, category listing, size/colour/price filters, exact labelled dimensions and package sizes from product pages, and per-store stock with restock dates. Works in any ikea.com market (`gb/en`, `de/de`, `il/he`, `us/en`…). |

### Interaction & output style

| Skill | Invoke | What it does |
| --- | --- | --- |
| [i-have-adhd](./skills/i-have-adhd/SKILL.md) | `/oz-skills:i-have-adhd` | Shapes Claude's output for a reader with ADHD — leads with the next action, numbers multi-step work, restates state across turns, suppresses tangents, gives concrete time estimates, and makes wins visible. Invoke with `/oz-skills:i-have-adhd`; stays on until you say "stop adhd mode". Vendored from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) and auto-synced. |
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
