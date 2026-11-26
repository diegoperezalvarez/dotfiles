---
name: draw-io-diagram-generator
description: Use when creating, editing, or generating draw.io files (.drawio, .drawio.svg, .drawio.png), flowcharts, system architecture, sequence, ER, UML class, low-level design (LLD) component diagrams, network and Yourdon / DeMarco data flow diagrams (DFDs). Output opens in the hediet.vscode-drawio VS Code extension.
---

# Draw.io Diagram Generator

Generate and edit draw.io files with valid mxGraph XML. Output opens directly in the [draw.io VS Code extension](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio) (`ext install hediet.vscode-drawio`).

## Workflow

1. **Scope**: infer diagram type, entities, relationships and output path from the request. Ask only if ambiguous. When editing, read the file first.
2. **Source**: start from a template in `assets/templates/` when one matches (see [Diagram types](#diagram-types)); otherwise use the skeleton below.
3. **Generate** the XML following the [XML rules](#xml-rules) and [Styles](#styles).
4. **Validate**: `python .agents/skills/draw-io-diagram-generator/scripts/validate-drawio.py <file.drawio>`. DFDs also need the checks in [DFDs](#data-flow-diagrams-yourdon--demarco).
5. **Deliver**: give the path, a one-sentence summary and the validator result. Tell the user to open the file in VS Code (the draw.io web or desktop app also works).

Skeleton (set `modified` to the current ISO 8601 timestamp):

```xml
<mxfile host="Electron" modified="" version="26.0.0">
  <diagram id="page-1" name="Page-1">
    <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" guides="1" tooltips="1"
                  connect="1" arrows="1" fold="1" page="1" pageScale="1"
                  pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- cells go here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## XML rules

- Cell ids `0` and `1` are required, come first, and are never reused. All other ids are unique within their page.
- Vertex: `vertex="1"`, `parent`, and an `<mxGeometry x y width height as="geometry"/>` child.
- Edge: `edge="1"`, `source` and `target` naming existing vertices, `parent`.
- Exception: floating edges (sequence lifelines) use `<mxPoint as="sourcePoint"/>` and `as="targetPoint"` inside `<mxGeometry>`.
- Children of a container use coordinates relative to it.
- Escape `&`, `<`, `>` in labels. Add `html=1` to any style whose label contains HTML.
- Snap to a 10px grid. Process boxes 120x60. A4 landscape canvas is 1169x827.
- Keep 40 or fewer cells per page. Multi-page files use multiple `<diagram>` elements.
- Give each page a title cell: `text;strokeColor=none;fillColor=none;fontSize=18;fontStyle=1`.

```xml
<mxCell id="svc" value="Order Service"
        style="rounded=1;whiteSpace=wrap;html=1;"
        vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry" />
</mxCell>
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;html=1;"
        edge="1" source="svc" target="db" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## Styles

Default to plain white (omit `fillColor`/`strokeColor`) for standard steps and neutral grey for start/end, decisions, and structural nodes. Reserve colour for semantic outcomes (e.g. Yes/No, success/error, external systems) rather than colouring every box.

| Purpose | fillColor | strokeColor |
|---|---|---|
| Process / step (default) | *(omit — white)* | *(omit — black)* |
| Start / end / decision / neutral | `#f5f5f5` | `#666666` (`fontColor=#333333`) |
| Yes / success | `#d5e8d4` | `#82b366` |
| No / error | `#f8cecc` | `#b85450` |
| Emphasis / client / external | `#dae8fc` | `#6c8ebf` |
| Warning / store | `#fff2cc` | `#d6b656` |
| Third-party / partner | `#e1d5e7` | `#9673a6` |

Core shape styles: process `rounded=1;whiteSpace=wrap;html=1;` · decision `rhombus;whiteSpace=wrap;html=1;` · start/end `ellipse;whiteSpace=wrap;html=1;` · database `shape=mxgraph.flowchart.database;whiteSpace=wrap;html=1;` · container `swimlane;startSize=30;fontStyle=1;` · connector `edgeStyle=orthogonalEdgeStyle;html=1;`

Full key catalog: `references/style-reference.md`. Shape names: `references/shape-libraries.md`.

## Diagram types

| Type | Template | Key points |
|---|---|---|
| Flowchart | `flowchart.drawio` | Start/end ellipse, process box, decision rhombus |
| Architecture | `architecture.drawio` | One swimlane per tier; services are children of their tier |
| Sequence | `sequence.drawio` | Lifelines are floating edges with `endArrow=none;dashed=1`; sync `endArrow=block;endFill=1`; return `dashed=1;endArrow=open;endFill=0` |
| ER | `er-diagram.drawio` | `shape=table` containers with `shape=tableRow` rows; `edgeStyle=entityRelationEdgeStyle` with `ERone` / `ERmany` / `ERzeroToOne` / `ERmandOne` arrows |
| UML class | `uml-class.drawio` | Swimlane class boxes; composition `startArrow=diamond;startFill=1`; inheritance `endArrow=block;endFill=0`; dependency `dashed=1;endArrow=open` |
| LLD (component internals) | `lld-minimal.drawio` | UML-style component frames, step boxes, cylinder tables, Valid/Invalid branches; one component per page. See `references/lld-notation.md` |
| Network, BPMN, other | none | Use `references/shape-libraries.md` |

### Data flow diagrams (Yourdon / DeMarco)

Keep these high level: one data flow page with a few processes, the stores they
use, and the datasets that move. Build them from a Python spec with `scripts/dfd_builder.py`, not raw XML.
Method and rules: `references/dfd-notation.md`. If a more granular picture is needed, try `references/lld-notation.md`.

- Page: `Data flow diagram` (3 to 6 processes, the stores, the arrows, the boundary and every external).
- Externals are blue rectangles outside the dashed boundary. Processes are grey ovals and stores are two parallel lines, inside it.
- Each arrow is one dataset from one source, with a plain-English name and a source tag (`[Postgres]`, `[S3]`, `[Redis]`). Never group datasets from different sources on one arrow.
- Draw each store or dataset once, in a single box, so the relations are visible. Avoid `duplicate=True`.
- Keep notes off the diagram. Give them as succinct bullets in your reply, unless a reader cannot follow the flow without one.
- Verify: `scripts/dfd_lint.py` (fix ERRORs; justify each WARN), `validate-drawio.py`, then a visual check of the page (see [references/visual-preview-check.md](references/visual-preview-check.md)). Stop the preview server and confirm cleanup before you finish; never detach it.

```python
import sys; sys.path.insert(0, ".agents/skills/draw-io-diagram-generator/scripts")
from dfd_builder import DfdDocument

doc = DfdDocument()
dfd = doc.page("dfd", "Data flow diagram", 1700, 1000)
dfd.title("Order system: data flow diagram")
dfd.boundary("Order system", 260, 120, 1160, 700)
dfd.external("customer", "Customer", 40, 260, kind="user")
dfd.process("take-order", "Take order", 420, 300)
dfd.store("orders", "Orders", 700, 560, w=200)
dfd.flow("customer", "take-order", "Order request", "Web form")
dfd.flow("take-order", "orders", "Order record", "Postgres", exit="bottom", entry="left")
doc.write("docs/order-dfd.drawio")   # writes, then runs dfd_lint and prints findings
```

## Editing existing files

- Read the file first; note existing ids, positions and parent hierarchy.
- Give new cells unique ids, and confirm every edge's source/target still exists after moving shapes.
- Add one shape without hand-editing XML: `python .agents/skills/draw-io-diagram-generator/scripts/add-shape.py docs/arch.drawio "New Service" 700 380`

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Blank file | Missing id `0` or `1` | Add both as the first cells |
| Edge not drawn | source/target id doesn't exist | Check ids match exactly |
| Shape in wrong place | Child coordinates are relative | Adjust relative to its container |
| "Compressed" diagram | base64-encoded mxGraphModel | In draw.io: File > Export > XML (uncompressed) |
| Style ignored | Typo in `shape=` name | Check `references/shape-libraries.md` |

## Reference files

| File | Contents |
|---|---|
| `references/drawio-xml-schema.md` | mxfile / mxGraphModel / mxCell attributes, coordinates, validation rules |
| `references/style-reference.md` | Style keys, allowed values, palette |
| `references/shape-libraries.md` | Shape library names and style strings |
| `references/dfd-notation.md` | DFD method, notation, rules, layout |
| `references/lld-notation.md` | LLD notation, layout rules, minimal example, reading walkthrough |
| `references/visual-preview-check.md` | Browser visual check: serving the preview, procedure, fixes for edge routing and labels |
| `scripts/README.md` | Script usage |
| `assets/templates/*.drawio` | Starter templates (including `lld-minimal.drawio`) |

