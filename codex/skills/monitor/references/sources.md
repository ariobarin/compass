# Sources

Read this provenance when auditing or revising Monitor, not during normal
monitoring.

Compass keeps waiting and unchanged observations outside model context while
retaining recovery ownership and terminal evidence. Native waits come first;
fixed report schemas, routine heartbeats, and redundant watcher loops are not
requirements.

- [SentinelBench, June 2026](https://www.microsoft.com/en-us/research/articles/sentinelbench-a-benchmark-for-long-running-monitoring-agents/) found change-aware local waiting cheaper and at least as successful as repeated model sleep.
- [A March 2026 Codex user trace](https://github.com/openai/codex/issues/13733) reports full-history replay under its HTTP setup; a [May correction](https://github.com/openai/codex/issues/13733#issuecomment-4483392890) says WebSocket transport sends only new messages.
- [Deep Researcher Agent, April 2026](https://arxiv.org/abs/2604.05854) reports OS-level monitoring and bounded memory across sustained multi-day experiments.
- [A Claude Code practitioner discussion, April 2026](https://www.reddit.com/r/ClaudeAI/comments/1shbg19/claude_codes_new_monitor_tool_lets_the_agent/) suggests carrying purpose, change, failure signal, and last known good context into a wakeup.
