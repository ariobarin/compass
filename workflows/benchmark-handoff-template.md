# Benchmark Handoff Template

Use this template when a benchmark run, recovery, or monitor may outlive the
current turn or move between controller and runner owners. Put the control
contract first. Evidence, logs, and history come after the first screen.

```text
objective: <exact result set to produce>
done means: <terminal, countable, comparable artifact condition>
runner owner: <thread, worker, process label, or explicit unassigned state>
controller owner: <parent thread or person keeping completion authority>
current next action: <the next command, monitor check, recovery action, or wait>
stop conditions: <only the concrete states that justify stopping>
validity contract: <arms, model, task set, timeout, scorer, stack, provenance>
recovery stance: invalid rows are debug-and-repair work until protocol evidence
  proves otherwise

state now:
- active labels:
- active processes:
- latest countable rows:
- invalid rows:
- missing rows:
- dominant error cluster:
- latest task ids:

runner instructions:
- own shell process, stdout, stderr, logs, immediate retries, and artifact
  preservation
- pause only the smallest poisoned labeled slice before it corrupts provenance
  or comparability
- keep unrelated comparable work moving
- ask the controller only after local recovery paths are exhausted or a
  benchmark-validity decision is truly needed

controller instructions:
- keep completion authority
- verify runner evidence before accepting status claims
- reroute failures into concrete next actions
- reject polished blocker reports while debug, repair, rerun, or isolation work
  remains

evidence and history:
- handoff path:
- artifact roots:
- monitor command:
- report command:
- relevant prior decisions:
```

Before sending the handoff, run:

```powershell
.\scripts\check-benchmark-handoff.ps1 -Path <handoff.md>
```

This template contains placeholders. Use `-AllowPlaceholders` only to check the
template shape, never for a real handoff.
