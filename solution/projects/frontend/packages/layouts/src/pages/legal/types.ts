/**
 * Legal page types
 */

export interface LegalPageSection {
  title: string;
  content: string | string[];
}

export interface LegalPageConfig {
  title: string;
  lastUpdated?: string | Date;
  sections: LegalPageSection[];
}

