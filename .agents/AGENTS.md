# Repository instructions

## Purpose and scope

This is a personal dotfiles repository managed as a **bare Git repository** with the home directory as its work tree. It contains Bash startup configuration and aliases, Python and shell helpers, dependency requirements, and reference notes. Changes should remain useful across machines and environments; do not assume every optional tool or platform is installed.

## Repository map

- `.bashrc` — interactive Bash configuration, prompt, completion, PATH, WSL handling, and `~/.venv` activation.
- `.bash_aliases` — shell aliases and functions, including helper-script aliases and optional AWS configuration.
- `.bash_scripts/` — Python and shell helpers for GTFS/GTFS-realtime, GIS, mapping, filtering, and dotfiles bootstrap.
- `.requirements.txt` — Python dependencies for personal data, geospatial, visualization, and agent workflows.
- `.notes.md` — personal reference material.
- `.github/README.md` — repository setup documentation.
- `.agents/AGENTS.md` — currently empty; reserved for agent-directory self-management.
- `.gitignore` — whitelist-style ignore file; tracked files require explicit `!` exceptions.

## Working conventions

- Preserve the bare-repository/home-directory installation model unless the task explicitly requires a model change.
- Keep shell startup code safe for interactive use. Avoid expensive operations, unnecessary output, and workarounds that require every machine to have an optional dependency.
- Quote Bash expansions that may contain spaces. Use `set -e` or explicit checks where appropriate, and guard platform-specific commands and files.
- Keep Python helpers explicit about inputs, outputs, and dependencies. Prefer packages already listed in `.requirements.txt`; update that file when introducing a runtime dependency.
- Do not add credentials, tokens, private keys, machine-specific paths, or account identifiers. Use environment variables or local, untracked configuration for secrets.
- Keep reusable instructions in root `AGENTS.md`. If shared skills or generated MCP configuration are added later, use `.agents/` as the canonical source.
- Keep agent-specific configuration in its native location. Do not duplicate it or invent synchronization infrastructure without a concrete need.

## Bootstrap safety

`.bash_scripts/dotfiles_init.sh` is destructive:

- It clones the repository as a bare repo into `~/.dotfiles`.
- It hides untracked files in the home directory via `status.showUntrackedFiles no`.
- It runs `git checkout -f` and overwrites matching files in `$HOME`.
- It refuses to run with `sudo` or as root.
- It makes executable `.sh` and `.py` files beneath `~/.bash_scripts`.

Review the script before running it. Back up any existing dotfiles that could conflict. Do not use bootstrap or other home-directory-modifying commands solely as validation.

## Validation

No automated test suite or CI workflow is currently present. Choose checks relevant to files changed:

- Bash: `bash -n .bashrc .bash_aliases .bash_scripts/*.sh`
- Python: `python -m compileall -q .bash_scripts`
- Helper behavior: run it only with a small, safe fixture and avoid commands that modify the home directory.
- Dependencies: verify `.requirements.txt` only in an environment where installation is appropriate.

Report exactly what was tested and what could not be tested.

## Adding files

Because `.gitignore` uses whitelist rules, add a matching exception for every new tracked top-level file or directory. Keep the root `AGENTS.md` exception explicit:

```gitignore
!AGENTS.md
```