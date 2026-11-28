'use client';

import {
  BookOpen,
  Component,
  Database,
  FlaskConical,
  Folder,
  FolderCode,
  FolderGit2,
  FolderInput,
  FolderOpen,
  FolderOutput,
  Image as ImageIcon,
  Languages,
  Package,
  Settings,
  Terminal,
  Workflow,
  type LucideIcon,
} from 'lucide-react';

/**
 * Conventional folder names → Lucide icon. Lookup is case-insensitive and
 * trimmed. Anything not in this map falls back to a generic folder icon.
 *
 * Designed to feel "right" across the common dev project layouts (Node,
 * Python, Go, Rust, Django, Next, Vite). Not exhaustive on purpose —
 * keeps the bundle light and the behaviour predictable.
 */
const SPECIAL_FOLDERS: Record<string, LucideIcon> = {
  src: FolderCode,
  source: FolderCode,
  lib: FolderCode,
  app: FolderCode,
  packages: Package,
  node_modules: Package,
  vendor: Package,
  public: FolderInput,
  static: FolderInput,
  assets: ImageIcon,
  images: ImageIcon,
  media: ImageIcon,
  dist: FolderOutput,
  build: FolderOutput,
  out: FolderOutput,
  '.next': FolderOutput,
  '.nuxt': FolderOutput,
  '.turbo': FolderOutput,
  docs: BookOpen,
  documentation: BookOpen,
  tests: FlaskConical,
  test: FlaskConical,
  __tests__: FlaskConical,
  __test__: FlaskConical,
  spec: FlaskConical,
  scripts: Terminal,
  bin: Terminal,
  config: Settings,
  configs: Settings,
  '.config': Settings,
  '.vscode': Settings,
  '.idea': Settings,
  '.git': FolderGit2,
  '.github': FolderGit2,
  '.gitlab': FolderGit2,
  '.husky': Workflow,
  '.circleci': Workflow,
  components: Component,
  component: Component,
  ui: Component,
  i18n: Languages,
  locale: Languages,
  locales: Languages,
  lang: Languages,
  translations: Languages,
  db: Database,
  database: Database,
  migrations: Database,
};

export interface ResolveFolderIconOptions {
  /** Folder display name (no path). */
  name: string;
  /** Open / closed state — only used for the *generic* folder fallback. */
  isExpanded?: boolean;
  /**
   * Optional override map. Wins over the built-in table. Keys are
   * matched case-insensitively after `trim()`.
   */
  overrides?: Record<string, LucideIcon>;
}

/**
 * Pick the right folder icon for `name`. Returns `Folder` / `FolderOpen`
 * for unknown names so callers can render the generic open/closed pair.
 */
export function resolveFolderIcon({
  name,
  isExpanded = false,
  overrides,
}: ResolveFolderIconOptions): LucideIcon {
  const key = name.trim().toLowerCase();
  if (overrides?.[key]) return overrides[key];
  const special = SPECIAL_FOLDERS[key];
  if (special) return special;
  return isExpanded ? FolderOpen : Folder;
}

export type FolderIconOverrides = Record<string, LucideIcon>;
