import type { CompassCatalogReader, CompassDocument, SkillSummary } from "../src/types.js";

export class EmbeddedCompassCatalog implements CompassCatalogReader {
  readonly documents: CompassDocument[];

  constructor(documents: CompassDocument[]) {
    this.documents = documents;
  }

  getProfile(): CompassDocument {
    return this.fetch("profile");
  }

  listSkills(): SkillSummary[] {
    return this.documents
      .filter(document => document.metadata.kind === "skill")
      .map(document => ({
        name: document.metadata.name,
        description: document.metadata.description,
        url: document.url
      }))
      .sort((left, right) => left.name.localeCompare(right.name));
  }

  getSkill(name: string): CompassDocument {
    return this.fetch(`skill:${name}`);
  }

  fetch(id: string): CompassDocument {
    const document = this.documents.find(candidate => candidate.id === id);
    if (!document) throw new Error(`Unknown Compass document: ${id}`);
    return document;
  }

  search(query: string): CompassDocument[] {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return this.documents;
    const terms = normalized.split(/\s+/).filter(Boolean);
    return this.documents
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
