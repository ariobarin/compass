# WebMCP Failure Rubric

Use this rubric to classify failures before changing code or evals.

## Primary Buckets

### Tool Fault

The tool is the owner when:

- It is not registered where the task needs it.
- It registers where it cannot succeed.
- It has the wrong schema, args, id source, page scope, or return shape.
- It executes but does not mutate or navigate as described.
- It returns unstructured text, stale data, or a swallowed opaque error.
- It violates the tool-shape contract.

### Stale Eval Expectation

The eval is the owner when:

- The site and tool behavior are correct.
- The expected value was frozen from old benchmark state.
- Live or local data legitimately differs.
- The mismatch is in `string_match`, exact content, counts, names, handles,
  routing data, or seeded state.

Do not patch eval expectations silently. Record the evidence and ask for human
sign-off when the expected answer changes.

### Agent Executor

The agent or executor is the owner when:

- The tool and eval are correct.
- The tool was available but the agent did not call it.
- The agent called the wrong tool or wrong args.
- The action adapter changed or mangled a tool call.
- The model ignored a valid return or observation.

### Infrastructure

The stack is the owner when:

- Broad site navigation fails.
- Ports, proxies, images, containers, auth, cookies, or base URLs are wrong.
- The test stack serves stale code.
- A background job or compose loop kills containers.
- Network, browser, or model backend failures dominate.

### Long-Run Drift

The run is no longer producing valid evidence when:

- Many rows fail with the same action-shape error.
- Worker stacks degrade after initial success.
- Login or auth state expires mid-run.
- Scheduler status is mistaken for completion.
- Result directories appear without terminal summaries.

## Compact Codes

Use these codes in notes or review comments when helpful.

| Code | Meaning |
|---|---|
| S1 | WebMCP supports imperative registration and declarative forms. |
| S2 | Imperative tools register with name, description, input schema, execute, annotations, and abort signal. |
| S3 | Declarative forms use real form fields and spec-defined attributes. |
| S4 | Declarative returns go through `respondWith` after `preventDefault`. |
| S6 | Annotations must match behavior. |
| S8 | Invented declarative attributes are ignored. |
| D2 | Descriptions are positive and behavioral. |
| D5 | Validate strictly in code and return useful errors. |
| D7 | Return after UI state is observable, except teardown-safe navigation returns first. |
| D8 | Tools are atomic and composable. |
| D10 | Registration follows page state. |
| B2 | Each tool has explicit scope and example page state in local notes or inventory. |
| B3 | Descriptions describe what the tool does, not instructions to the agent. |
| B6 | Login is not a registered tool. |
| B7 | Generic declarative workflows use list/action pairs. |
| B11 | Navigation and mutation return one structured value, never an MCP content envelope. |
| B12 | Hidden fake forms are not valid declarative tools. |
| A1 | Colocate tools with page kinds when possible. |
| A2 | The current page is the implicit first argument. |
| A3 | Prefer declarative forms when a real form exists. |
| A5 | Drive the page widget when UI state matters. |
| T1 | Form to results page. |
| T2 | List current page rows. |
| T3 | Act on a listed row by id. |
| T4 | Sort or filter without navigation. |
| T5 | Read DOM state such as sections or tables. |
| T6 | Open modal or expand panel. |
| T7 | Navigate to known sibling page with teardown-safe return. |
| F1 | Spec-shape mistake. |
| F2 | Cross-tool consistency failure. |
| F3 | Scope or navigation-flow drift. |

## Decision Rules

- If the tool fails under direct browser invocation, start with tool or infra.
- If direct invocation works and persists, but the benchmark reward fails, check
  stale eval and agent executor before editing the tool.
- If failures cluster by site or port, check infra.
- If failures cluster by tool family, check tool shape and registration.
- If failures cluster by model action text, check executor parsing or prompt.
- If rows lack terminal artifacts, do not score them as task failures.
