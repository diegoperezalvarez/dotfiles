# draw-io Scripts

Utility scripts for working with `.drawio` diagram files.

## Requirements

- Python 3.8+
- No external dependencies (uses standard library only: `xml.etree.ElementTree`, `argparse`, `json`, `sys`, `pathlib`)

## Scripts

### `validate-drawio.py`

Validates the XML structure of a `.drawio` file against required constraints.

**Usage**

```bash
python scripts/validate-drawio.py <path-to-diagram.drawio>
```

**Examples**

```bash
# Validate a single file
python scripts/validate-drawio.py docs/architecture.drawio

# Validate all drawio files in a directory
for f in docs/**/*.drawio; do python scripts/validate-drawio.py "$f"; done
```

**Checks performed**

| Check | Description |
|-------|-------------|
| Root cells | Verifies id="0" and id="1" cells are present in every diagram page |
| Unique IDs | All `mxCell` id values are unique within a diagram |
| Edge connectivity | Every edge has valid `source` and `target` attributes pointing to existing cells |
| Geometry | Every vertex cell has an `mxGeometry` child element |
| Parent chain | Every cell's `parent` attribute references an existing cell id |
| XML well-formedness | File is valid XML |

**Exit codes**

- `0` — Validation passed
- `1` — One or more validation errors found (errors printed to stdout)

---

### `add-shape.py`

Adds a new shape (vertex cell) to an existing `.drawio` diagram file.

**Usage**

```bash
python scripts/add-shape.py <diagram.drawio> <label> <x> <y> [options]
```

**Arguments**

| Argument | Required | Description |
|----------|----------|-------------|
| `diagram` | Yes | Path to the `.drawio` file |
| `label` | Yes | Text label for the new shape |
| `x` | Yes | X coordinate (pixels from top-left) |
| `y` | Yes | Y coordinate (pixels from top-left) |

**Options**

| Option | Default | Description |
|--------|---------|-------------|
| `--width` | `120` | Shape width in pixels |
| `--height` | `60` | Shape height in pixels |
| `--style` | `"rounded=1;whiteSpace=wrap;html=1;"` | draw.io style string |
| `--diagram-index` | `0` | Index of the diagram page (0-based) |
| `--dry-run` | false | Print the new cell XML without modifying the file |

**Examples**

```bash
# Add a basic rounded box
python scripts/add-shape.py docs/flowchart.drawio "New Step" 400 300

# Add a custom styled shape
python scripts/add-shape.py docs/flowchart.drawio "Decision" 400 400 \
  --width 160 --height 80 \
  --style "rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"

# Preview without writing
python scripts/add-shape.py docs/architecture.drawio "Service X" 600 200 --dry-run
```

**Output**

Prints the new cell id on success:
```
Added shape id="auto_abc123" to page 0 of docs/flowchart.drawio
```

---

### `dfd_builder.py`

Importable builder for Yourdon / DeMarco data flow diagrams. Writes the notation styles, the `dfd=` role
keys used by `dfd_lint.py`, edge anchors and duplicate stores, then runs the linter on save.

**Usage**

```bash
# Regenerate the DFD template (data flow diagram)
python scripts/dfd_builder.py --example assets/templates/data-flow-diagram.drawio
```

**API (from a spec script)**

| Call | Draws |
|------|-------|
| `doc = DfdDocument()`, `p = doc.page(id, name, w, h)` | A new page |
| `p.title(text)`, `p.subtitle(text)` | Title (`fontSize=18`, passes `validate-drawio.py`) and subtitle |
| `p.boundary(name, x, y, w, h)` | Dashed system boundary |
| `p.external(id, name, x, y, kind="service"\|"user", sub=)` | Blue rectangle outside the boundary |
| `p.process(id, name, x, y, d=150, sub=)` | Grey oval (process) |
| `p.store(id, name, x, y, duplicate=False, io="")` | Two-line data store; duplicates get ids `<id>-dup1`, ... and a `*` |
| `p.flow(src, tgt, name, detail="", via=[(x, y)], exit=, entry=)` | Arrow with a name and a short note; `exit`/`entry` take `left`, `right`, `top`, `bottom` or `(fx, fy)` |
| `p.legend(x, y)` | Notation legend |
| `doc.write(path, lint=True)` | Writes the file, runs `dfd_lint`, returns the error count |

---

### `dfd_lint.py`

Checks a DFD against the simple rules. Works on builder output (role keys) and on hand-drawn
diagrams (shape heuristics: ellipse = process, two-line store, unrounded blue rectangle = external).

```bash
python scripts/dfd_lint.py docs/my-dfd.drawio            # exit 1 on ERRORs
python scripts/dfd_lint.py docs/my-dfd.drawio --strict   # exit 1 on ERRORs or WARNs
```

| Rule | Severity | Check |
|------|----------|-------|
| R1 | ERROR | Every arrow touches a process |
| R2 | ERROR | Every arrow is named |
| R3 | ERROR | Every process has an input and an output arrow |
| R4 | ERROR | Externals outside the boundary; processes and stores inside |
| R5 | WARN | Stores are written and read (unless `dfdIo=sink`/`source`) |
| R6 | WARN | No arrow passes through an unrelated shape |

---

### `render-preview.py`

Writes an HTML page that renders every diagram page, for a visual check.

```bash
python scripts/render-preview.py docs/my-dfd.drawio --out /tmp/preview/preview.html
cd /tmp/preview && python -m http.server 8765 --bind 127.0.0.1
# open http://127.0.0.1:8765/preview.html; each page is in <div id="d0">, <div id="d1">, ...
```

The page loads the draw.io viewer script from `viewer.diagrams.net`. Rendering happens in the browser;
the diagram XML stays in the local HTML. Delete the preview afterwards.

---

### `preview-serve.py`

Renders a diagram with `render-preview.py` into a temporary folder and serves it on `127.0.0.1` so the
integrated browser can open it over `http` (`file://` is blocked there). Run it attached and stop it to end
the preview. The temporary folder is removed on exit, including on SIGTERM.

```bash
python scripts/preview-serve.py docs/my-dfd.drawio --port 8765
# open http://127.0.0.1:8765/preview.html
```

Run it as an attached process. Stop it with Ctrl+C or `stop_bash` and read the stop message: it prints
`Removed temporary folder`. Do not detach it. A SIGKILL leaves the temporary folder behind; see
[the reference note](../references/visual-preview-check.md#shutdown-and-cleanup-required) for the manual removal step.
See [references/visual-preview-check.md](../references/visual-preview-check.md) for the full procedure and fixes.

---

## Common Workflows

### Validate before committing

```bash
# Validate all diagrams
find . -name "*.drawio" -not -path "*/node_modules/*" | \
  xargs -I{} python scripts/validate-drawio.py {}
```

### Quickly add a placeholder node

```bash
python scripts/add-shape.py docs/architecture.drawio "TODO: Service" 800 400 \
  --style "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;"
```

### Check a template is valid

```bash
python scripts/validate-drawio.py .agents/skills/draw-io-diagram-generator/assets/templates/flowchart.drawio
```

### Build and check a data flow diagram

```bash
python docs/build_my_dfd.py                    # your spec script; writes the .drawio and runs dfd_lint
python scripts/validate-drawio.py docs/my-dfd.drawio
python scripts/render-preview.py docs/my-dfd.drawio --out /tmp/preview/preview.html
```
