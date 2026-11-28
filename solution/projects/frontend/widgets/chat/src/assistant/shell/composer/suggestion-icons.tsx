import { BarChart3, FileText, Filter, ListChecks, PenLine, Search, Sparkles, Wand2 } from 'lucide-react';
import type { ReactNode } from 'react';

/** The starter rows' glyphs, by key. A row names one with `{ prompt, icon: 'search' }`; an unknown key draws none. */
const ICONS = {
  sparkles: Sparkles,
  search: Search,
  summarize: FileText,
  write: PenLine,
  tidy: ListChecks,
  chart: BarChart3,
  filter: Filter,
  agent: Wand2,
} as const;

export type SuggestionIconKey = keyof typeof ICONS;
export const SUGGESTION_ICON_KEYS = Object.keys(ICONS) as SuggestionIconKey[];

export function suggestionIcon(key: string): ReactNode {
  const Icon = (ICONS as Record<string, (typeof ICONS)[SuggestionIconKey]>)[key];
  return Icon ? <Icon className="size-4 shrink-0 text-muted-foreground" aria-hidden /> : null;
}
