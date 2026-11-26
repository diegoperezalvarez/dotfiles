# draw.io Style Reference

The `style` attribute is a semicolon-delimited list of `key=value` pairs, for example `rounded=1;fillColor=#dae8fc;`. Keys are case-sensitive and unknown keys are ignored. For shape names see [shape-libraries.md](shape-libraries.md).

## Common keys (vertices and edges)

| Key | Values | Notes |
| --- | ------ | ----- |
| `fillColor`, `strokeColor`, `fontColor` | `#hex` / `none` | Use the palette below |
| `fontSize` | integer | Default 11 |
| `fontStyle` | bitmask | 1 bold, 2 italic, 4 underline, 8 strikethrough; add to combine (3 = bold italic) |
| `fontFamily` | string | Default Helvetica |
| `align`, `verticalAlign` | `left`/`center`/`right`, `top`/`middle`/`bottom` | Text alignment |
| `strokeWidth` | float | Border or line width |
| `dashed`, `dashPattern` | `1`, `8 4` | Dashed line |
| `spacing`, `spacingTop`/`Bottom`/`Left`/`Right` | integer | Text padding |
| `html` | `1` | Required for HTML in labels |
| `whiteSpace` | `wrap` | Wrap long labels |
| `overflow` | `hidden` | Clip text to the shape |
| `opacity` | 0-100 | |
| `labelPosition`, `verticalLabelPosition` | `left`/`right`, `top`/`bottom` | Move the label outside the shape |

## Vertex keys

| Key | Values | Notes |
| --- | ------ | ----- |
| `shape` | name | Overrides the default rectangle |
| `rounded`, `arcSize` | `1`, 0-50 | Corner radius is a percentage |
| `aspect` | `fixed` | Lock aspect ratio |
| `rotation` | degrees | |
| `container`, `collapsible` | `0`/`1` | Container for child cells; collapse toggle |
| `startSize` | px | Header height for swimlanes and tables |
| `swimlaneHead`, `swimlaneBody` | `0`/`1` | Show or hide swimlane parts (table rows set both to `0`) |
| `gradientColor`, `gradientDirection` | `#hex`, `north`/`south`/`east`/`west` | |
| `sketch` | `1` | Hand-drawn look |

## Edge keys

| Key | Values | Notes |
| --- | ------ | ----- |
| `edgeStyle` | see below | Routing |
| `rounded`, `curved` | `0`/`1` | Corner style |
| `exitX`/`exitY`, `entryX`/`entryY` | 0.0-1.0 | Anchor on source or target (0,0 is top-left) |
| `exitDx`/`exitDy`, `entryDx`/`entryDy` | px | Offset from the anchor |
| `endArrow`, `startArrow` | see below | Arrow head or tail |
| `endFill`, `startFill` | `0`/`1` | Filled or hollow head |
| `endSize`, `startSize` | px | Head size |
| `labelBackgroundColor` | `#hex` | Background behind the label |

| `edgeStyle` | Routing | Use for |
| ----------- | ------- | ------- |
| `none` | Straight line | Direct links |
| `orthogonalEdgeStyle` | Right-angle turns | Flowcharts, architecture |
| `elbowEdgeStyle` | Single elbow | Sequence messages |
| `entityRelationEdgeStyle` | ER routing | ER diagrams |

| Arrow | Look | Use for |
| ----- | ---- | ------- |
| `block` | Filled triangle | Directed arrow; hollow (`endFill=0`) for UML inheritance |
| `open` | Open chevron | Light arrow, async, dependency |
| `classic` | Classic arrow | draw.io default, DFD flows |
| `none` | No head | Undirected line |
| `diamond` | Diamond | Aggregation (`Fill=0`) or composition (`Fill=1`) |
| `oval` | Dot | |
| `ERone`, `ERmandOne`, `ERmany`, `ERzeroToOne`, `ERzeroToMany`, `ERoneToMany` | Crow's foot | ER cardinality |

## Colour palette

Default to plain white (no `fillColor`/`strokeColor`) for standard steps and neutral grey for start/end, decisions, and structural nodes. Use colour sparingly for semantic meaning (outcomes, externals, warnings) rather than colouring every shape.

| Meaning | Fill | Stroke |
| ------- | ---- | ------ |
| Process / step (default) | *(omit)* | *(omit)* |
| Start / end / decision / neutral | `#f5f5f5` | `#666666` (`fontColor=#333333`) |
| Yes / success | `#d5e8d4` | `#82b366` |
| No / error / critical | `#f8cecc` | `#b85450` |
| User / client / external | `#dae8fc` | `#6c8ebf` |
| Warning / store | `#fff2cc` | `#d6b656` |
| Third-party / partner | `#e1d5e7` | `#9673a6` |
| Queue / async | `#ffe6cc` | `#d79b00` |
| Gateway / proxy | `#dae8fc` | `#0050ef` |

DFD colours and styles come from `scripts/dfd_builder.py`; see [dfd-notation.md](dfd-notation.md).

## Common style strings

```text
Box:           rounded=1;whiteSpace=wrap;html=1;
Start / End:   ellipse;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#333333;fontStyle=1;
Decision:      rhombus;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontColor=#333333;
Yes / Success: rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;
No / Error:    rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;
Database:      shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;fillColor=#f5f5f5;strokeColor=#666666;
Swimlane pool: shape=pool;startSize=30;horizontal=1;fillColor=#f5f5f5;strokeColor=#999999;
Swimlane lane: swimlane;startSize=30;fillColor=#ffffff;strokeColor=#999999;
Connector:     edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;
Bold arrow:    edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeWidth=2;
Dashed:        edgeStyle=orthogonalEdgeStyle;dashed=1;endArrow=open;endFill=0;strokeColor=#666666;
Invisible:     edgeStyle=none;strokeColor=none;endArrow=none;
```

UML and ER relationship strings are in [shape-libraries.md](shape-libraries.md).
