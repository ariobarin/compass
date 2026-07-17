# WebMCP Carried Skill Pack

These WebMCP skills are carried with Compass but are not installed globally.
They are project-specific guidance until repeated cross-repository use justifies
promotion.

## Opt In

Copy only the needed skill folder from `carried/webmcp/skills/` into the target
repository's project-local skill home, normally:

```text
<target-repo>/.agents/skills/<skill-name>/
```

Use the target repository's own convention when it differs. Keep the skill close
to the WebMCP code, fixtures, browser stack, and eval surface it describes.

The pack contains:

- `webmcp-tool-authoring`
- `webmcp-verify-tool`
- `webmcp-eval-triage`

Do not add these names to Compass global skill manifests merely for convenience.
Promote a skill only after evidence shows the same capability, trigger, and
contract are useful across unrelated repositories.
