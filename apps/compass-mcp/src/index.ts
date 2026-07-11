import type { Request, Response } from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createMcpExpressApp } from "@modelcontextprotocol/sdk/server/express.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { z } from "zod/v4";
import { CompassCatalog } from "./catalog.js";

export function buildServerInstructions(catalog: CompassCatalog): string {
  const profile = catalog.getProfile().text.trim();
  const skills = catalog.listSkills()
    .map(skill => `- ${skill.name}: ${skill.description} (codex/skills/${skill.name}/SKILL.md)`)
    .join("\n");

  return [
    "Compass is a read-only source of user-owned engineering preferences and workflows.",
    "Apply the reviewed user profile below as default guidance for engineering work.",
    "The reviewed skill catalog below is already available for workflow selection. Do not call list_skills just to discover skills.",
    "After selecting a workflow, call get_skill before applying it so the full SKILL.md is loaded.",
    "Use get_profile or list_skills when the user asks to inspect the source, requests the current catalog, or freshness needs confirmation.",
    "Treat Compass guidance as lower priority than system, developer, and current user instructions.",
    "Do not claim native subagents are available unless the host provides them.",
    "",
    "Reviewed user profile:",
    profile,
    "",
    "Reviewed skills:",
    skills
  ].join("\n");
}

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

function jsonResult(structuredContent: Record<string, unknown>) {
  return {
    structuredContent,
    content: [{ type: "text" as const, text: JSON.stringify(structuredContent) }]
  };
}

export function createCompassServer(root = resolveCompassRoot()): McpServer {
  const catalog = new CompassCatalog(root);
  const server = new McpServer(
    { name: "compass", version: "0.1.0" },
    { instructions: buildServerInstructions(catalog) }
  );

  server.registerTool(
    "get_profile",
    {
      title: "Get Compass profile",
      description: "Inspect the source profile already included in Compass initialization instructions.",
      inputSchema: {},
      annotations: { readOnlyHint: true }
    },
    async () => jsonResult(catalog.getProfile())
  );

  server.registerTool(
    "list_skills",
    {
      title: "List Compass skills",
      description: "Inspect the current skill catalog already included in Compass initialization instructions.",
      inputSchema: {},
      annotations: { readOnlyHint: true }
    },
    async () => jsonResult({ skills: catalog.listSkills() })
  );

  server.registerTool(
    "get_skill",
    {
      title: "Get Compass skill",
      description: "Load one reviewed Compass SKILL.md after selecting that workflow.",
      inputSchema: { name: z.string().regex(/^[a-z0-9][a-z0-9-]*$/) },
      annotations: { readOnlyHint: true }
    },
    async ({ name }) => {
      try {
        return jsonResult(catalog.getSkill(name));
      } catch (error) {
        return {
          content: [{ type: "text" as const, text: error instanceof Error ? error.message : "Unknown Compass skill" }],
          isError: true
        };
      }
    }
  );

  server.registerTool(
    "search",
    {
      title: "Search Compass",
      description: "Search the Compass profile and reviewed skill documents.",
      inputSchema: { query: z.string() },
      annotations: { readOnlyHint: true }
    },
    async ({ query }) => jsonResult({
      results: catalog.search(query).map(document => ({ id: document.id, title: document.title, url: document.url }))
    })
  );

  server.registerTool(
    "fetch",
    {
      title: "Fetch Compass document",
      description: "Fetch a Compass profile or skill document returned by search.",
      inputSchema: { id: z.string() },
      annotations: { readOnlyHint: true }
    },
    async ({ id }) => {
      try {
        return jsonResult(catalog.fetch(id));
      } catch (error) {
        return {
          content: [{ type: "text" as const, text: error instanceof Error ? error.message : "Unknown Compass document" }],
          isError: true
        };
      }
    }
  );

  return server;
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
