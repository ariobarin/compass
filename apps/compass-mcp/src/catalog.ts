import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import type { CompassCatalogReader, CompassDocument, SkillSummary } from "./types.js";

const REPOSITORY_URL = "https://github.com/ariobarin/compass";

function unquote(value: string): string {
  const trimmed = value.trim();
  if (trimmed.startsWith('"') && trimmed.endsWith('"')) {
    try {
      return JSON.parse(trimmed) as string;
    } catch {
      return trimmed.slice(1, -1);
    }
  }
  return trimmed;
}

function frontmatterValue(text: string, key: string): string | undefined {
  const frontmatter = text.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/)?.[1];
  if (!frontmatter) return undefined;
  const match = frontmatter.match(new RegExp(`^${key}:\\s*(.+)$`, "m"));
  return match ? unquote(match[1]) : undefined;
}

export class CompassCatalog implements CompassCatalogReader {
  readonly root: string;
  readonly profilePath: string;
  readonly skillsPath: string;

  constructor(root: string) {
    this.root = path.resolve(root);
    this.profilePath = path.join(this.root, "codex", "AGENTS.md");
    this.skillsPath = path.join(this.root, "codex", "skills");

    if (!existsSync(this.profilePath)) {
      throw new Error(`Compass profile not found: ${this.profilePath}`);
    }
    if (!existsSync(this.skillsPath)) {
      throw new Error(`Compass skills directory not found: ${this.skillsPath}`);
    }
  }

  getProfile(): CompassDocument {
    return {
      id: "profile",
      title: "Compass user profile",
      text: readFileSync(this.profilePath, "utf8"),
      url: `${REPOSITORY_URL}/blob/main/codex/AGENTS.md`,
      metadata: { kind: "profile", source: "codex/AGENTS.md" }
    };
  }

  listSkills(): SkillSummary[] {
    return readdirSync(this.skillsPath, { withFileTypes: true })
      .filter(entry => entry.isDirectory())
      .map(entry => {
        const skillFile = path.join(this.skillsPath, entry.name, "SKILL.md");
        if (!existsSync(skillFile)) return null;
        const text = readFileSync(skillFile, "utf8");
        const name = frontmatterValue(text, "name") ?? entry.name;
        const description = frontmatterValue(text, "description") ?? "";
        return {
          name,
          description,
          url: `${REPOSITORY_URL}/blob/main/codex/skills/${encodeURIComponent(entry.name)}/SKILL.md`
        };
      })
      .filter((skill): skill is SkillSummary => skill !== null)
      .sort((left, right) => left.name.localeCompare(right.name));
  }

  getSkill(name: string): CompassDocument {
    const skill = this.listSkills().find(item => item.name === name);
    if (!skill) throw new Error(`Unknown Compass skill: ${name}`);
    const skillFile = path.join(this.skillsPath, name, "SKILL.md");
    return {
      id: `skill:${name}`,
      title: name,
      text: readFileSync(skillFile, "utf8"),
      url: skill.url,
      metadata: { kind: "skill", name, description: skill.description }
    };
  }

  fetch(id: string): CompassDocument {
    if (id === "profile") return this.getProfile();
    if (id.startsWith("skill:")) return this.getSkill(id.slice("skill:".length));
    throw new Error(`Unknown Compass document: ${id}`);
  }

  search(query: string): CompassDocument[] {
    const normalized = query.trim().toLowerCase();
    const documents = [this.getProfile(), ...this.listSkills().map(skill => this.getSkill(skill.name))];
    if (!normalized) return documents;
    const terms = normalized.split(/\s+/).filter(Boolean);
    return documents
      .map(document => {
        const haystack = `${document.title}\n${document.metadata.description ?? ""}\n${document.text}`.toLowerCase();
        const score = terms.reduce((total, term) => total + (haystack.includes(term) ? 1 : 0), 0);
        return { document, score };
      })
      .filter(result => result.score > 0)
      .sort((left, right) => right.score - left.score || left.document.title.localeCompare(right.document.title))
      .map(result => result.document);
  }
}
