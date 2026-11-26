# draw.io Shape Libraries

Shape names and style strings by diagram type. Style keys, arrow types and the palette are in [style-reference.md](style-reference.md). Add `whiteSpace=wrap;html=1;` to any string below.

## General and flowchart

| Shape | Style |
| ----- | ----- |
| Rectangle | *(default)* |
| Rounded rectangle, process | `rounded=1;` |
| Ellipse, start/end | `ellipse;` |
| Diamond, decision | `rhombus;` |
| Hexagon | `shape=hexagon;` |
| Cloud | `shape=cloud;` |
| Cylinder, database | `shape=cylinder3;` |
| Note | `shape=note;` |
| Document | `shape=document;` |
| Parallelogram | `shape=parallelogram;perimeter=parallelogramPerimeter;` |
| Data (I/O) | `shape=mxgraph.flowchart.io;` |
| Predefined process | `shape=mxgraph.flowchart.predefined_process;` |
| Manual input / operation | `shape=mxgraph.flowchart.manual_input;` / `shape=mxgraph.flowchart.manual_operation;` |
| Database | `shape=mxgraph.flowchart.database;` |
| Multi-document | `shape=mxgraph.flowchart.multi-document;` |
| Off-page connector | `shape=mxgraph.flowchart.off_page_connector;` |
| On-page connector | `ellipse;` at 30x30 |
| Preparation, delay, display | `shape=mxgraph.flowchart.preparation;` / `.delay;` / `.display;` |
| Internal storage | `shape=mxgraph.flowchart.internal_storage;` |
| Sort, extract, merge, or | `shape=mxgraph.flowchart.sort;` / `.extract;` / `.merge;` / `.or;` |
| Annotation | `shape=mxgraph.flowchart.annotation;` |

## UML

| Shape | Style |
| ----- | ----- |
| Actor | `shape=mxgraph.uml.actor;` |
| Use case | `ellipse;` |
| System boundary, class box | `swimlane;startSize=30;` |
| Component | `shape=component;align=left;spacingLeft=36;` |
| Package, node, artifact | `shape=mxgraph.uml.package;` / `.node;` / `.artifact;` |
| Lifeline | `shape=umlLifeline;startSize=40;` |
| Activation box | `shape=umlActivation;` |
| Initial state | `ellipse;aspect=fixed;fillColor=#000000;strokeColor=#000000;` |
| State | `rounded=1;arcSize=50;` |
| Final state | `shape=doubleEllipse;fillColor=#000000;strokeColor=#000000;` |
| Fork / join | `shape=mxgraph.uml.fork_or_join;fillColor=#000000;` |

Relationships (all `edgeStyle=orthogonalEdgeStyle;html=1;` plus):

| Relationship | Add |
| ------------ | --- |
| Inheritance | `endArrow=block;endFill=0;` |
| Implementation | `dashed=1;endArrow=block;endFill=0;` |
| Association | `endArrow=open;endFill=0;` |
| Dependency | `dashed=1;endArrow=open;endFill=0;` |
| Aggregation | `startArrow=diamond;startFill=0;endArrow=none;` |
| Composition | `startArrow=diamond;startFill=1;endArrow=none;` |

Sequence messages use `edgeStyle=elbowEdgeStyle;elbow=vertical;html=1;` plus `endArrow=block;endFill=1;` (sync), `endArrow=open;endFill=0;` (async), or `dashed=1;endArrow=open;endFill=0;` (return). A self-call adds `exitX=1;exitY=0.3;entryX=1;entryY=0.5;`.

Class boxes: a `swimlane` parent (`fontStyle=1;align=center;startSize=40`) with `text;html=1;align=left;verticalAlign=top;spacingLeft=5;whiteSpace=wrap;overflow=hidden;rotatable=0;` child cells whose `parent` is the class id. Use `&#xa;` for line breaks. See `assets/templates/uml-class.drawio`. Sequence diagrams: `assets/templates/sequence.drawio` draws lifelines as dashed `endArrow=none` edges instead of `umlLifeline` shapes.

## Entity relationship

Tables use `shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;fontStyle=1;`. Each row is a `shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;` child of the table. Each cell in a row is a `shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;overflow=hidden;` child of the row (bold for PK, italic for type). Worked XML is in `assets/templates/er-diagram.drawio`.

Relationships use `edgeStyle=entityRelationEdgeStyle;html=1;` plus:

| Cardinality | Add |
| ----------- | --- |
| One-to-one | `startArrow=ERmandOne;endArrow=ERmandOne;startFill=1;endFill=1;` |
| One-to-many | `startArrow=ERmandOne;endArrow=ERmany;startFill=1;endFill=1;` |
| Zero-to-many | `startArrow=ERmandOne;endArrow=ERzeroToMany;startFill=1;endFill=0;` |
| Zero-to-one | `startArrow=ERmandOne;endArrow=ERzeroToOne;startFill=1;endFill=0;` |
| Many-to-many | `startArrow=ERmany;endArrow=ERmany;startFill=1;endFill=1;` |

## Network

| Shape | Style |
| ----- | ----- |
| Server | `shape=server;` |
| Web server, database server | `shape=mxgraph.network.web_server;` / `shape=mxgraph.network.database;` |
| Laptop, desktop, mobile | `shape=mxgraph.network.laptop;` / `.desktop;` / `.mobile;` |
| Router | `shape=mxgraph.cisco.routers.router;` |
| Switch | `shape=mxgraph.cisco.switches.workgroup_switch;` |
| Firewall | `shape=mxgraph.cisco.firewalls.firewall;` |
| Internet, load balancer | `shape=mxgraph.network.internet;` / `shape=mxgraph.network.load_balancer;` |

## Cloud

AWS uses `shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.<name>;` with `<name>` one of `ec2`, `lambda`, `s3`, `rds`, `api_gateway`, `cloudfront`, `elb`, `sqs`, `sns`, `dynamodb`, `ecs`, `eks`. Groups use `shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc;` (or `group_region`).

| Azure | Style |
| ----- | ----- |
| App Service, Function App | `shape=mxgraph.azure.app_service;` / `.function_apps;` |
| SQL Database, Blob Storage | `shape=mxgraph.azure.sql_database;` / `.blob_storage;` |
| API Management, Service Bus, AKS | `shape=mxgraph.azure.api_management;` / `.service_bus;` / `.aks;` |

| GCP | Style |
| --- | ----- |
| Cloud Run, Functions, SQL, Storage | `shape=mxgraph.gcp2.cloud_run;` / `.cloud_functions;` / `.cloud_sql;` / `.cloud_storage;` |
| GKE, Pub/Sub, BigQuery | `shape=mxgraph.gcp2.container_engine;` / `.cloud_pubsub;` / `.bigquery;` |

## Kubernetes

`shape=mxgraph.kubernetes.<name>;` with `<name>` one of `pod`, `deploy`, `svc`, `ing`, `cm`, `secret`, `pv`, `ns`, `node`.

## BPMN

BPMN events and tasks use `shape=mxgraph.bpmn.shape;` with a perimeter and `symbol`:

| Shape | Add |
| ----- | --- |
| Start event | `perimeter=mxPerimeter.ellipsePerimeter;symbol=general;verticalLabelPosition=bottom;` |
| End event | `perimeter=mxPerimeter.ellipsePerimeter;symbol=terminate;verticalLabelPosition=bottom;` |
| Task | `perimeter=mxPerimeter.rectanglePerimeter;symbol=task;` |
| Sub-process | `perimeter=mxPerimeter.rectanglePerimeter;symbol=subProcess;` |
| Exclusive gateway | `perimeter=mxPerimeter.rhombusPerimeter;symbol=exclusiveGw;` |
| Parallel gateway | `perimeter=mxPerimeter.rhombusPerimeter;symbol=parallelGw;` |

Pools and lanes are `shape=pool;startSize=30;horizontal=1;` and `swimlane;startSize=30;`. Sequence flow is `edgeStyle=orthogonalEdgeStyle;html=1;endArrow=block;endFill=1;`; message flow adds `dashed=1;` and `endFill=0;`.

## Mockup

`shape=mxgraph.mockup.forms.button;`, `.forms.text1;` (input), `.forms.checkbox;`, `.forms.comboBox;`, `.containers.browser;`, `.containers.smartphone;`, `.containers.list;`, `.containers.table;`.

## Data flow diagrams

Generate these with `scripts/dfd_builder.py`, which sets the `dfd=` role keys that `scripts/dfd_lint.py` checks. Styles live in `dfd_builder.STYLES`; method and rules are in [dfd-notation.md](dfd-notation.md).
