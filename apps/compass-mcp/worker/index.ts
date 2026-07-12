import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { createCompassMcpServer } from "../src/server.js";
import { embeddedDocuments } from "./generated-catalog.js";
import { EmbeddedCompassCatalog } from "./embedded-catalog.js";

const catalog = new EmbeddedCompassCatalog(embeddedDocuments);

function jsonResponse(body: unknown, status = 200, headers?: HeadersInit): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", ...headers }
  });
}

export async function handleCompassRequest(request: Request): Promise<Response> {
  const url = new URL(request.url);

  if (url.pathname === "/healthz" && request.method === "GET") {
    return jsonResponse({ ok: true, service: "compass-mcp" });
  }

  if (url.pathname !== "/mcp") {
    return jsonResponse({ error: "Not found" }, 404);
  }

  if (request.method !== "POST") {
    return jsonResponse({
      jsonrpc: "2.0",
      error: { code: -32000, message: "Method not allowed" },
      id: null
    }, 405, { allow: "POST" });
  }

  const server = createCompassMcpServer(catalog);
  const transport = new WebStandardStreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true
  });

  try {
    await server.connect(transport);
    return await transport.handleRequest(request);
  } catch (error) {
    console.error("Compass MCP request failed", error);
    return jsonResponse({
      jsonrpc: "2.0",
      error: { code: -32603, message: "Internal server error" },
      id: null
    }, 500);
  }
}

export default {
  fetch: handleCompassRequest
};
