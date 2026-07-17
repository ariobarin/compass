import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod/v4";
import type { CompassDocument, CompassCatalogReader } from "./types.js";

export function buildServerInstructions(catalog: CompassCatalogReader): string {
  const profile = catalog.getProfile().text.trim();
  const skills = catalog.listSkills()
    .map(skill => `- ${skill.name}: ${skill.description} (codex/skills/${skill.name}/SKILL.md)`)
    .join("\n");

  return [
    "Compass supplies read-only user-owned engineering preferences and workflows to regular ChatGPT.com chat mode.",
    "Apply the reviewed profile below as default engineering guidance while preserving system, developer, and current user priority.",
    "Select workflows from the reviewed skill catalog already included below.",
    "Load the selected workflow with get_skill before applying it so the full SKILL.md is present.",
    "Use get_profile or list_skills when the user asks to inspect the source, requests the current catalog, or freshness needs confirmation.",
    "Treat subagents as available only when the current host exposes them.",
    "Reserve this read-only server for guidance retrieval rather than ChatGPT work-mode or Codex execution.",
    "",
    "Reviewed user profile:",
    profile,
    "",
    "Reviewed skills:",
    skills
  ].join("\n");
}

function jsonResult(structuredContent: Record<string, unknown>) {
  return {
    structuredContent,
    content: [{ type: "text" as const, text: JSON.stringify(structuredContent) }]
  };
}

function documentResult(document: CompassDocument) {
  return jsonResult(document);
}

export function createCompassMcpServer(catalog: CompassCatalogReader): McpServer {
  const server = new McpServer(
    { name: "compass", version: "0.2.0" },
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
    async () => documentResult(catalog.getProfile())
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
        return documentResult(catalog.getSkill(name));
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
        return documentResult(catalog.fetch(id));
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
