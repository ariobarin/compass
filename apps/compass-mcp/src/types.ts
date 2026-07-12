export type CompassDocument = {
  id: string;
  title: string;
  text: string;
  url: string;
  metadata: Record<string, string>;
};

export type SkillSummary = {
  name: string;
  description: string;
  url: string;
};

export interface CompassCatalogReader {
  getProfile(): CompassDocument;
  listSkills(): SkillSummary[];
  getSkill(name: string): CompassDocument;
  fetch(id: string): CompassDocument;
  search(query: string): CompassDocument[];
}
