import assert from "node:assert/strict";
import { once } from "node:events";
import { request } from "node:http";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import { startServer } from "../src/index.js";

process.env.COMPASS_ROOT = process.env.COMPASS_ROOT ?? fileURLToPath(new URL("../../..", import.meta.url));
process.env.HOST = "127.0.0.1";
process.env.PORT = "33117";
process.env.ALLOWED_HOSTS = "127.0.0.1,compass.example.test";

function getHealthStatus(host: string): Promise<number | undefined> {
  return new Promise((resolve, reject) => {
    const req = request({
      host: "127.0.0.1",
      port: 33117,
      path: "/healthz",
      method: "GET",
      headers: { host }
    }, res => {
      res.resume();
      res.on("end", () => resolve(res.statusCode));
    });
    req.on("error", reject);
    req.end();
  });
}

const httpServer = startServer();
if (!httpServer.listening) await once(httpServer, "listening");

const client = new Client({ name: "compass-smoke", version: "0.1.0" });
const transport = new StreamableHTTPClientTransport(new URL("http://127.0.0.1:33117/mcp"));

try {
  assert.equal(await getHealthStatus("compass.example.test"), 200);

  await client.connect(transport);
  const tools = await client.listTools();
  assert.deepEqual(
    tools.tools.map(tool => tool.name).sort(),
    ["fetch", "get_profile", "get_skill", "list_skills", "search"]
  );

  const profile = await client.callTool({ name: "get_profile", arguments: {} });
  assert.equal(profile.isError, undefined);
  assert.match(JSON.stringify(profile), /Pull requests/);

  const skills = await client.callTool({ name: "list_skills", arguments: {} });
  assert.equal(skills.isError, undefined);
  assert.match(JSON.stringify(skills), /input-token-economy/);

  const skill = await client.callTool({ name: "get_skill", arguments: { name: "input-token-economy" } });
  assert.equal(skill.isError, undefined);
  assert.match(JSON.stringify(skill), /Input Token Economy/);

  const search = await client.callTool({ name: "search", arguments: { query: "input token" } });
  assert.match(JSON.stringify(search), /skill:input-token-economy/);

  console.log("compass mcp smoke: ok");
} finally {
  await client.close();
  httpServer.close();
  await once(httpServer, "close");
}
