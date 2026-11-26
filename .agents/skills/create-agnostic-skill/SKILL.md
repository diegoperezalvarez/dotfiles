---
name: create-agnostic-skill
description: Create, migrate, or validate agent-agnostic skills that work in any AI coding agent (Copilot, Claude Code, Codex, Cursor, Gemini CLI). Use when asked to add a new skill, write a SKILL.md, move skills out of .claude/skills or .cursor, or make a repo's agent setup vendor-neutral. Follows the agentskills.io spec with .agents/skills/ as the single canonical location.
---

# Create an agent-agnostic skill

Store each skill once in `.agents/skills/<name>/`. Agents that do not scan that folder get symlinks. Never keep a second copy.

Based on the [Agent-Agnostic Repository Guide](https://gist.github.com/davidgibsonp/337be9b80b3f03eccd188235c287bb05) and the [Agent Skills spec](https://agentskills.io/specification).

## Classify first

| The asset is | Example | Where it goes |
|---|---|---|
| Portable (same format in every agent) | `SKILL.md`, `AGENTS.md` | `.agents/` or repo root; symlink from agent folders |
| Generated (same data, different format) | MCP config | Canonical copy in `.agents/`; a script renders each agent's format |
| Agent-specific | `.cursor/rules/*.mdc`, `.claude/settings.json`, `.claude/agents/*.md` | Leave it in the agent's own folder |
| Sensitive business data | Client names, project details, internal URLs, commercial or confidential information | `.copilot/skills/<name>/`; never in `.agents/` |

**IMPORTANT:** `.agents/skills/` must not contain sensitive business data or information. Any skill that contains it goes in `.copilot/skills/` instead and is never committed. Before you write a skill, check its content, references and assets.

Apart from that, a skill is always **portable**. If the request is really a rule that should always apply, or project context, put it in `AGENTS.md` instead of a skill.

## Layout

```
.agents/
  skills/<name>/          # shared, committed
    SKILL.md              # required
    references/           # optional: long docs, loaded on demand
    scripts/              # optional: helper scripts the skill runs
    assets/               # optional: templates and example files
  skills-local/<name>/    # private, gitignored
```

## Steps

1. **Check for an existing skill.** Look in `.agents/skills/`, `.claude/skills/` and `.cursor/` before you create one. Extend an existing skill when it fits.
2. **Pick the name.** Use lowercase letters, numbers and hyphens, with at most 64 characters, no leading or trailing hyphen and no `--`. The name must **match the directory name**.
3. **Write `SKILL.md`:**

   ```markdown
   ---
   name: <name>
   description: <What it does, then "Use when ..." trigger phrases. Max 1024 chars.>
   ---

   # <Title>

   <Imperative, step-by-step instructions for the agent.>
   ```

   - `name` and `description` are the only required fields. The optional fields are `license`, `compatibility`, `metadata` (a key-value map) and `allowed-tools`. Do not add agent-specific keys.
   - Agents choose a skill from its `description`, so name the concrete tasks, file types and keywords that should trigger it.
   - Keep the file under 500 lines. Move long detail into `references/*.md` and link it with a relative path, for example `[schema](references/schema.md)`.
   - Use relative paths only. Do not write machine-specific absolute paths, secrets or the name of a particular agent's tools. Describe the action instead, for example "search the codebase", not a tool name.
4. **Add scripts only when the agent would otherwise rewrite the same code each time.** A script should run on its own, print clear errors and declare its dependencies.
5. **Expose the skill to agents that do not read `.agents/skills/`.** Copilot and Codex read it natively. Claude Code and Cursor need a symlink:

   ```bash
   for d in .claude/skills .cursor/skills; do
     mkdir -p "$d" && ln -sfn "../../.agents/skills/<name>" "$d/<name>"
   done
   ```

   If the repo has `.agents/scripts/link-skills.sh`, run that instead. Only create the symlink folders for agents the repo actually uses.
6. **Validate:**
   - The frontmatter parses, and `name` equals the directory name.
   - `wc -l SKILL.md` is under 500.
   - Every relative link resolves.
   - Every symlink resolves: `ls -L .claude/skills/<name>/SKILL.md`.
   - Optionally run `skills-ref validate .agents/skills/<name>` if [skills-ref](https://github.com/agentskills/agentskills) is installed.
7. **Make sure git tracks the skill.** Run `git check-ignore -v .agents/skills/<name>/SKILL.md`. If the file is ignored, add an exception. Whitelist-style ignore files (`*` first) need `!.agents/` as well as `!.agents/**`, because git cannot re-include files inside an ignored directory. Commit the skill directory and any symlinks. Never commit `skills-local/`.

## Migrating existing skills

- When `.claude/skills/<name>/` contains real files, move it with `git mv` to `.agents/skills/<name>/`, then replace the original with a symlink (step 5).
- When a skill exists in more than one agent folder, merge the copies into one in `.agents/skills/` and delete the others.
- Leave `.cursor/rules/*.mdc` where they are. If another agent needs that knowledge, copy it into `AGENTS.md`.
- Third-party skills: `npx skills add <repo>@<skill> -y` installs into `.agents/skills/` and creates the symlinks.

## Rules

- Edit skills only in `.agents/skills/`. Never edit them through `.claude/skills/` or `.cursor/skills/`.
- Use one skill per job. Split a skill that does unrelated jobs.
- Do not add sync scripts, MCP generation or pre-commit hooks unless the repo already needs them.
