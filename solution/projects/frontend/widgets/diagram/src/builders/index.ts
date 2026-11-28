/**
 * Mermaid Diagram Builders
 *
 * Declarative, type-safe builders for creating Mermaid diagrams.
 *
 * @example
 * ```tsx
 * import {
 *   FlowDiagram,
 *   SequenceDiagram,
 *   JourneyDiagram,
 *   useStylePresets,
 *   useBoxColors
 * } from '@djangocfg/widget-diagram';
 *
 * function MyDiagram() {
 *   const presets = useStylePresets();
 *   const boxes = useBoxColors();
 *
 *   // Flow diagram
 *   const flow = FlowDiagram<'A' | 'B'>({ direction: 'LR' });
 *   flow.node('A').rect('Start');
 *   flow.edge('A').to('B').solid();
 *   flow.style.define('highlight', presets.success);
 *
 *   // Sequence diagram
 *   const { d, rect } = SequenceDiagram({
 *     Alice: 'participant',
 *     Bob: 'actor',
 *   });
 *   rect(boxes.primary, () => {
 *     d.Alice.sync.Bob.msg('Hello!');
 *   });
 *
 *   // Journey diagram
 *   const journey = JourneyDiagram({ title: 'User Flow' });
 *   journey.section('Start').task('Open app', 5, 'User');
 * }
 * ```
 *
 * @module Mermaid/builders
 */

// Core
export { DiagramStore, type DiagramStoreOptions } from './core/DiagramStore';
export { sanitizeLabel, toNodeId, escapeQuoted, formatLabel } from './core/sanitize';
export * from './core/types';

// Theme hooks and utilities (re-exported from @djangocfg/ui-core/styles/palette)
export {
  useThemePalette,
  useStylePresets,
  useBoxColors,
  hslToHex,
  hslToRgbString,
  hslToRgba,
  type ThemePalette,
  type StyleColors,
  type StylePresets,
  type BoxColors,
} from './core/theme';

// FlowDiagram
export { FlowDiagram, STYLE_PRESETS } from './FlowDiagram';
export type {
  FlowDiagramOptions,
  FlowDiagramBuilder,
  NodeBuilder,
  EdgeBuilder,
  EdgeEndBuilder,
  StyleBuilder,
  SubgraphBuilder,
} from './FlowDiagram';

// SequenceDiagram
export { SequenceDiagram } from './SequenceDiagram';
export type {
  ParticipantsObject,
  SequenceDiagramOptions,
  SequenceDiagramBuilder,
  MessageBuilder,
  MessageArrows,
  MessageTarget,
  MessageAction,
  NoteBuilder,
  ActivationBuilder,
} from './SequenceDiagram';

// JourneyDiagram
export { JourneyDiagram } from './JourneyDiagram';
export type {
  JourneyDiagramOptions,
  JourneyDiagramBuilder,
  SectionBuilder,
  TaskDefinition,
} from './JourneyDiagram';
