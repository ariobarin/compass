# Understanding Check Hook

On `UserPromptSubmit`, focuses direct prompts such as "do you understand what I
mean", `dykwim`, `dywim`, and `ykwim` on answering the understanding check.

The guidance still allows repo inspection or web search when more context is
needed to answer accurately.

Set `CODEX_PORTABLE_DISABLE_UNDERSTANDING_CHECK=1` to disable this focus.
