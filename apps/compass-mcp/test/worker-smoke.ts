import assert from "node:assert/strict";
import { handleCompassRequest } from "../worker/index.js";

let requestId = 0;

async function rpc(method: string, params: Record<string, unknown>): Promise<Record<string, unknown>> {
  requestId += 1;
  const response = await handleCompassRequest(new Request("https://compass.ariobarin.com/mcp", {
    method: "POST",
    headers: {
      accept: "application/json, text/event-stream",
      "content-type": "application/json"
    },
    body: JSON.stringify({ jsonrpc: "2.0", id: requestId, method, params })
  }));
  assert.equal(response.status, 200);
  return await response.json() as Record<string, unknown>;
}

const health = await handleCompassRequest(new Request("https://compass.ariobarin.com/healthz"));
assert.equal(health.status, 200);
assert.deepEqual(await health.json(), { ok: true, service: "compass-mcp" });

const initialized = await rpc("initialize", {
  protocolVersion: "2025-06-18",
  capabilities: {},
  clientInfo: { name: "compass-worker-smoke", version: "0.1.0" }
});
assert.match(JSON.stringify(initialized), /compass/);

const tools = await rpc("tools/list", {});
assert.deepEqual(
  ((tools.result as { tools: Array<{ name: string }> }).tools).map(tool => tool.name).sort(),
  ["fetch", "get_profile", "get_skill", "list_skills", "search"]
);

const search = await rpc("tools/call", { name: "search", arguments: { query: "input token" } });
assert.match(JSON.stringify(search), /skill:input-token-economy/);

console.log("compass worker smoke: ok");
