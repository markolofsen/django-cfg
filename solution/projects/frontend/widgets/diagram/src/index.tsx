/**
 * Two halves that belong together and ship apart.
 *
 * WRITING a diagram — `FlowDiagram`, `SequenceDiagram`, `JourneyDiagram` — is
 * a pure string function a server pass, a test or a CLI can call, and it costs
 * nothing. DRAWING one loads `mermaid`, which unpacks to ~84 MB, so `Mermaid`
 * arrives behind `React.lazy` and the library only when a diagram mounts.
 *
 * `@djangocfg/widget-media/diagram` is the OTHER renderer and is not a
 * duplicate of this one. It parses with `beautiful-mermaid` (~2 MB) and covers
 * flowchart, sequence, state, class and ER, falling back to the source for the
 * rest — the right trade for a chat transcript, where most messages carry no
 * diagram at all. This one carries the full parser: gantt, mindmap, pie and
 * everything else, for a surface whose job IS the diagram.
 *
 * Pick by what the surface is for, and do not import both into one app.
 */

'use client';

export type { MermaidProps } from './types';

/**
 * The renderer, behind its dynamic import.
 *
 * ONE lazy boundary, not two: this file used to wrap `Mermaid.client` in its
 * own `React.lazy` with a hand-rolled spinner while `lazy.tsx` wrapped the same
 * module again with the shared placeholder. Two boundaries around one module
 * split nothing extra and gave the same component two different loading states
 * depending on which name a consumer imported.
 */
export { LazyMermaid, LazyMermaid as Mermaid, LazyMermaid as default } from './lazy';

// Re-export builders for declarative diagram construction
export {
  // Core
  DiagramStore,
  sanitizeLabel,
  toNodeId,
  // Theme hooks
  useThemePalette,
  useStylePresets,
  useBoxColors,
  // FlowDiagram
  FlowDiagram,
  STYLE_PRESETS,
  // SequenceDiagram
  SequenceDiagram,
  // JourneyDiagram
  JourneyDiagram,
} from './builders';

export type {
  // Core types
  DiagramStoreOptions,
  FlowDirection,
  NodeShape,
  ParticipantType,
  TaskScore,
  // Theme types
  ThemePalette,
  StyleColors,
  StylePresets,
  BoxColors,
  // FlowDiagram types
  FlowDiagramOptions,
  FlowDiagramBuilder,
  NodeBuilder,
  EdgeBuilder,
  StyleBuilder,
  // SequenceDiagram types
  ParticipantsObject,
  SequenceDiagramOptions,
  SequenceDiagramBuilder,
  // JourneyDiagram types
  JourneyDiagramOptions,
  JourneyDiagramBuilder,
  SectionBuilder,
} from './builders';
