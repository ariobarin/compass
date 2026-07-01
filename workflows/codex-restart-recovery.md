# Codex Restart Recovery Workflow

Use this workflow on Windows hosts where Codex should recover useful work after
an unexpected restart without polling forever.

This is a machine setup workflow. It does not make live `automations/` state
portable, and it does not preserve in-memory model turns. It creates a local
scheduled task that runs after logon, checks saved Codex session files once per
Windows boot, and resumes only sessions that look unfinished.

## Behavior

The recovery script:

- records the current boot in `$CODEX_HOME\restart-recovery`;
- exits immediately if the current boot was already processed;
- scans sessions last touched before boot and within a bounded lookback window;
- selects only sessions where the latest user turn has no final assistant
  answer after it;
- skips sessions whose latest user turn was intentionally aborted;
- treats a persisted recovery prompt without completion as retryable;
- resumes one session by default, or more only when `-MaxThreads` is explicit;
- marks the boot handled only after selected sessions resume successfully;
- writes resume logs under `$CODEX_HOME\restart-recovery`.

The default prompt is:

```text
continue, the computer restarted for some reason
```

## Install

From a trusted Compass checkout:

```powershell
.\scripts\codex-restart-recovery.ps1 -InstallTask
```

The install command registers a Windows logon scheduled task named
`\Compass\Codex Restart Recovery`, delayed by 2 minutes. It also marks the
current boot as already handled so installing the task does not wake older
sessions from the same boot.

Use explicit bounds when a host needs different recovery behavior. Raising
`-MaxThreads` opts into broader recovery fanout:

```powershell
.\scripts\codex-restart-recovery.ps1 -InstallTask -LookbackHours 12 -MaxThreads 3 -DelayMinutes 3
```

## Preview

Before enabling a host, preview candidates without resuming anything:

```powershell
.\scripts\codex-restart-recovery.ps1 -DryRun
```

To mark the current boot handled without installing or resuming:

```powershell
.\scripts\codex-restart-recovery.ps1 -MarkCurrentBootHandled
```

## Remove

```powershell
.\scripts\codex-restart-recovery.ps1 -UninstallTask
```

## Related Host Setup

The recovery task only runs after a user session exists. For unattended restart
recovery, Windows still needs a signed-in user session. A separate host setup can
auto-login, launch the Codex app, and lock the workstation again after startup.

Keep those machine credentials and scheduled-task instances local. Commit only
the reviewed script and workflow here.
