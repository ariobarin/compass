import type { Request, Response } from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createMcpExpressApp } from "@modelcontextprotocol/sdk/server/express.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { CompassCatalog } from "./catalog.js";
import { createCompassMcpServer } from "./server.js";

export function resolveCompassRoot(): string {
  if (process.env.COMPASS_ROOT) return path.resolve(process.env.COMPASS_ROOT);
  const here = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(here, "../../..");
}

export function resolveAllowedHosts(): string[] | undefined {
  const configured = process.env.ALLOWED_HOSTS;
  if (configured === undefined) return undefined;

  const hosts = [...new Set(configured.split(",").map(host => host.trim()).filter(Boolean))];
  if (hosts.length === 0) {
    throw new Error("ALLOWED_HOSTS must contain at least one hostname");
  }
  return hosts;
}

export function createCompassServer(root = resolveCompassRoot()): McpServer {
  return createCompassMcpServer(new CompassCatalog(root));
}

export function startServer() {
  const host = process.env.HOST ?? "127.0.0.1";
  const port = Number.parseInt(process.env.PORT ?? "3000", 10);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error(`Invalid PORT: ${process.env.PORT}`);
  }

  const app = createMcpExpressApp({ host, allowedHosts: resolveAllowedHosts() });
  app.get("/healthz", (_req, res) => res.json({ ok: true }));
  app.post("/mcp", async (req: Request, res: Response) => {
    const server = createCompassServer();
    const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
    res.on("close", () => {
      void transport.close();
      void server.close();
    });

    try {
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
    } catch (error) {
      console.error("Compass MCP request failed", error);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: "2.0",
          error: { code: -32603, message: "Internal server error" },
          id: null
        });
      }
    }
  });
  app.get("/mcp", (_req, res) => res.status(405).json({
    jsonrpc: "2.0",
    error: { code: -32000, message: "Method not allowed" },
    id: null
  }));
  app.delete("/mcp", (_req, res) => res.status(405).json({
    jsonrpc: "2.0",
    error: { code: -32000, message: "Method not allowed" },
    id: null
  }));

  return app.listen(port, host, () => {
    console.error(`Compass MCP listening on http://${host}:${port}/mcp`);
  });
}

const entrypoint = process.argv[1] ? path.resolve(process.argv[1]) : "";
if (entrypoint === fileURLToPath(import.meta.url)) {
  startServer();
}
