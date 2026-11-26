# Low-level Data-flow-Diagram (LLD) in draw.io

An LLD shows how one component works internally: its processing steps,
the data structures it reads and writes, the external services it calls, and the
branches a record can take. Use it when a DFD
(see [dfd-notation.md](dfd-notation.md)) is too high level.

For a LLD, emphasise the data itself: each field's name, type, whether it is required or nullable, and the shape the code enforces (for example, enums, type hints, validation aliases and explicit checks). Show every expected pattern, check and weak connection, including the expected shape of each response object. Mark a weak connection with a dashed edge, or with a dashed border (`dashed=1`) on a box whose shape is not guaranteed.

Keep each LLD focused on one end-to-end process. In a data-specific LLD, do not include other systems unless they materially change the data returned. For example, it is not necessary to draw a diagram for every http status code, simply follow the process of the expected process, noting only significant diverges that change the output.

For LLDs, you may skip the number of cells requirement. Do not put notes on the diagram unless the flow cannot be followed without them. Give notes, gaps and assumptions as succinct bullet points in your textual response at the end.

Name the source of every dataset: the data store or service it is read from or written to (`Postgres`, `Redis`, `S3`, `SQS`, an API). Put it in the store or external label, or on the edge (`csv_data [S3]`). Keep separate datasets in separate boxes and on separate edges, even when they feed the same step. Never merge datasets that come from different sources into one structure box.

| Need | Use |
|---|---|
| What moves between systems | DFD |
| Order of steps in one process | Flowchart |
| Lower-level steps, tables, branches | **LLD (this file)** |

Starter file: `assets/templates/lld-minimal.drawio`.

## Notation

| Element | draw.io style | Meaning |
|---|---|---|
| Component frame | `shape=umlFrame;whiteSpace=wrap;html=1;width=240;height=30;` | One unit of code or process. Title format: `«name» P: Purpose` |
| Step (process) | `rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#333333;` | One operation. Label: `«function_name» Plain-English action` |
| Data store | `shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;` | A table, file or cache |
| Structure box | `verticalAlign=top;align=left;overflow=fill;html=1;whiteSpace=wrap;` with a bold, underlined header row holding the name, a horizontal rule (`<hr>`), then one line per field | A record, schema or class. List fields with types, e.g. `licence_number: str`. Add `dashed=1` for a shape that is not guaranteed (see the `record` box in the template) |
| External service, input or output | `html=1;dropTarget=0;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;` | A system outside the component |
| Log sink | Same style as a data store (`shape=cylinder3`). Label: `«CloudWatch»` then `Logger: <what is logged>` | Where an invalid or rejected record ends up when it is only logged, such as `Logger: invalid_file` |
| Silent drop | `verticalAlign=top;align=left;overflow=fill;html=1;whiteSpace=wrap;dashed=1;` with one centred line, for example `Silently drops duplicate records` | An outcome the code does not report back to the caller. The record just disappears (it may still be logged, say so in the box) |
| Breakout bubble | `ellipse;whiteSpace=wrap;html=1;shapeInside=1;fontStyle=1` at 30x30, label is a single letter (`A`, `B`, ...) | A break in a long edge. Used in pairs with the same letter, see [Breakouts](#breakouts) |
| Note | `text;whiteSpace=wrap;html=1;fontStyle=2;` with the label starting `note:` | Rare. Only when the diagram cannot be read without it. Otherwise put it in the reply |

Edges:

- Solid arrow with an edge label `Valid` (or the success outcome) for the main path.
- Dashed arrow with `Invalid` (or the failure outcome) for branches that stop.
- Dashed arrow from a step to a silent drop box, labelled with the rule that triggers it (for example `Duplicates`). Use `edgeStyle=none;html=1;endArrow=block;endFill=1;dashed=1;`.
- Plain arrow with a short verb label (`insert`, `lookup`) for data movement. Label the arrow between two steps with the data it carries when that is not obvious (for example `csv_data`).
- Double-headed arrow (`startArrow=block;startFill=1;endArrow=block;endFill=1;`) when a step both writes to and reads from an external, for example `put in bucket / read when finished`.
- Use `edgeStyle=orthogonalEdgeStyle;html=1;` on every edge, except breakout and silent drop edges, which are short and use `edgeStyle=none;html=1;`.
- Each success end has a solid return edge to the caller (the trigger step), labelled with the response it sends.

### Breakouts

Use a breakout bubble when drawing the edge in full would cross other edges or repeat the same destination (for example, several steps that all log to the same sink). Instead of one long edge:

1. Put a bubble next to each source step and join them with a short edge. The label (`Invalid`, `update`) sits on this edge and the arrow head points at the bubble.
2. Put one bubble with the **same letter** next to the destination and join it with a short solid arrow into the destination (`edgeStyle=none;html=1;endArrow=block;endFill=1;`).
3. Use a new letter for each destination. A letter has exactly one destination bubble and one or more source bubbles.

Read a letter as one edge per source bubble: source step, then bubble `A`, then the destination of the `A` bubble that points at it. Keep bubbles for crossings and repeats only. Do not use them where a short direct edge is clear.

## Layout rules

- One component per page. Put its steps inside its frame, its stores beside them and any external connections outside the frame.
- Try to keep to as few cells as possible that fully describe the data flow.
- Avoid edge crossings. Where two edges must cross, or several edges would run to the same destination, replace the long edge with a [breakout](#breakouts).
- The main flow should be sequential going top-down.
- Snap to a 10px grid. Children of a frame use coordinates relative to the frame.
- Give each page the title cell from the skeleton (`fontSize=18`).
- Keep step labels to the function name and one plain-English line. Leave out parameters, timeouts, thread counts and headers unless they change the outcome.
- Do not use rhombus (flowchart decision) shapes. Model each check as a step box with the question as its label, and label its branches where required.

## Minimal example

The template follows the rough steps below:

```text
[Title: Minimal LLD example]
[POST API /submit] --> [Frame: «Ingestion» P: Record ingestion]
    («validate_record» Valid record format?) --Invalid--> [CloudWatch: Logger, logs invalid records]
    («validate_record») --Valid--> («validate_record» Malware check) <--put / read--> [S3 ClamAV bucket]
    («Malware check») --Infected File--> [CloudWatch: Logger, invalid_file]
    («Malware check») --csv_data--> («csv_data_check» Schema registration check) --Valid--> («duplicate_record_check» Check for duplicates)
    («duplicate_record_check») - - Duplicates - -> [dashed: Silently drops duplicate records]
    («duplicate_record_check») --> («store_record» Insert new or update) --Valid--> [record_store: postgres]
    («store_record») --Invalid--> (A) ... (A) --> [CloudWatch: Logger, logs invalid records]   <- breakout
    note: example only, not a real component
```

Open `assets/templates/lld-minimal.drawio` to edit it directly. Validate with:

```bash
python .agents/skills/draw-io-diagram-generator/scripts/validate-drawio.py <file.drawio>
```

## Walkthrough: reading an LLD page

Read an LLD page in this order:

1. **Trigger.** How the component starts, such as a schedule, an event or an API call.
2. **Fetch.** The external source and the request shape. Note any retry or error behaviour.
3. **Validate.** Each check in sequence. Every branch should lead to an outcome.
4. **Reference checks.** Lookups against another service or table, for example "does this licence exist". Record which fields are used as keys.
5. **Duplicates.** The rule that decides whether two records are the same, and what happens to the second one. If the code drops it without any report or log, draw it as a silent drop.
6. **Store.** The upsert or insert, and the table written. Note whether the write updates an existing row or only creates new ones.
7. **Outcomes.** Every terminal end: stored, rejected, logged, silently dropped or aborted. Follow each breakout letter to its matching bubble.

Write each step as one short sentence. List anything the diagram cannot show, such as a
branch that is not reachable in practice or a column that is never populated, as bullets
in your reply.

## Checklist

- Every edge's `source` and `target` exists on the same page.
- Every breakout letter has exactly one destination bubble (arrow into a store or step) and at least one source bubble.
- Every `Invalid` or failure branch ends at a named outcome.
- A record the code drops without reporting it back ends at a dashed silent drop box, not at a log sink.
- Every table or external service appears once, with the same label everywhere on the page, so one dataset is one box.
- Every dataset names its source (Postgres, Redis, S3, ...). Datasets from different sources are not grouped.
- Known gaps are bullets in the reply, not diagram cells or hidden in labels.
- The page validates with `scripts/validate-drawio.py`.
