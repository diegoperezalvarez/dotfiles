# Dotfiles

Personal dotfiles kept in a **bare git repo**: git dir `~/.dotfiles`, work tree `$HOME`. The remote is **public** on GitHub, so treat every committed line as published.

## Running git

`.bashrc` returns early in non-interactive shells, so the `dotfiles` alias is not defined for agents. Use:

```bash
git --git-dir="$HOME/.dotfiles" --work-tree="$HOME" <command>
```

- `status.showUntrackedFiles` is `no`. To see new files, add `--untracked-files=all` and a path, e.g. `status --short --untracked-files=all .scripts`.
- Never run `git add -A`, `add .` or `clean` here. They act on the whole home directory.
- `.gitignore` is a whitelist: `*`, then `!` exceptions. A new top-level folder needs **both** `!.name/` and `!.name/**`. Without the first, git cannot see inside the folder and new files are silently ignored. A new top-level file needs `!.name`.

## What is tracked

| Path | What it is | Rules |
|---|---|---|
| `.bashrc` | Interactive shell setup: Homebrew, history, prompt, completion, `PATH`, WSL browser, activates `~/.venv` | Keep it fast and silent. Guard optional tools and files (`[ -x … ] &&`, `[ -f … ] &&`) as the existing lines do. Must work on Linux, WSL and macOS. |
| `.bash_aliases` | Aliases and small functions, sourced by `.bashrc` | Keep the sections (`wsl things`, `Scripts`, `Notebooks`, `General`, `Other aliases`). Use single quotes when an alias contains `$(...)` or `$var`, so it expands when run, not when the file is sourced. |
| `.scripts/` | Standalone Python CLIs, plus `init.sh` | See below. |
| `.requirements.txt` | Packages for `~/.venv`, grouped by comment heading | Add top-level packages only. Note large transitive deps in a trailing comment, as the existing lines do. |
| `.notes.md` | Personal command cheat sheet, searched with `qnotes <pattern>` | Keep one heading per command, with the command in backticks, so `qnotes` finds it. Replace account IDs, hosts and URLs with `XXXX` placeholders. |
| `.github/README.md` | Symlink to `../.notes.md` so GitHub shows the notes | Edit `.notes.md`, never the symlink. |
| `.agents/skills/<name>/` | Agent skills, shared across agents | Follow the `create-agnostic-skill` skill. No client, project or employer-confidential content (this repo is public); such skills go in untracked `~/.copilot/skills/`. |

Local, untracked overrides: `~/.aws/.bash_aliases` (sourced if present). Put machine-specific or sensitive settings in files like this, never in tracked files.

## `.scripts/`

- Each script is a standalone CLI: `#!/usr/bin/env python` shebang, module docstring explaining usage, `argparse`, errors to stderr with a non-zero exit.
- Scripts run in `~/.venv`. Use packages already in `.requirements.txt`, and add any new runtime dependency there.
- To add a script: create it, `chmod +x` it, add an alias under `# Scripts` in `.bash_aliases`, and check that git sees it (`status --untracked-files=all .scripts`).
- `init.sh` is the bootstrap, and it is destructive. It clones the bare repo and runs `checkout -f`, which overwrites matching files in `$HOME`. It refuses to run as root. Never run it to test something.

## Validate

```bash
bash -n ~/.bashrc ~/.bash_aliases ~/.scripts/init.sh
~/.venv/bin/python -c 'import ast,sys; [ast.parse(open(f).read(), f) for f in sys.argv[1:]]' ~/.scripts/*.py
~/.venv/bin/python ~/.scripts/<script>.py --help   # for any script you changed
```

There are no tests or CI. Run scripts only on small throwaway inputs. Before committing, run the git `diff` and check it for secrets, account IDs, internal URLs and client names.
