import assert from "node:assert/strict";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const endpoint = new URL(process.env.COMPASS_MCP_URL ?? "https://compass.ariobarin.com/mcp");
const healthUrl = new URL("/healthz", endpoint);
const health = await fetch(healthUrl);
assert.equal(health.status, 200);
assert.deepEqual(await health.json(), { ok: true, service: "compass-mcp" });

const client = new Client({ name: "compass-remote-smoke", version: "0.1.0" });
const transport = new StreamableHTTPClientTransport(endpoint);

try {
  await client.connect(transport);
  const tools = await client.listTools();
  assert.deepEqual(
    tools.tools.map(tool => tool.name).sort(),
    ["fetch", "get_profile", "get_skill", "list_skills", "search"]
  );

  const profile = await client.callTool({ name: "get_profile", arguments: {} });
  assert.equal(profile.isError, undefined);
  assert.match(JSON.stringify(profile), /Pull requests/);

  console.log(`compass remote smoke: ok (${endpoint.href})`);
} finally {
  await client.close();
}
