// Adapted from jalcoui (MIT) — github.com/jal-co/ui

export { DiffViewer } from './DiffViewer';
export { DIFF_TONE_CLASSES } from './types';
export {
  diffLines,
  parseUnifiedPatch,
  computeStats as computeDiffStats,
  lineNumberWidth as diffLineNumberWidth,
} from './utils/computeDiff';
export { useDiff } from './hooks/useDiff';

export type {
  DiffLayout,
  DiffLine,
  DiffLineType,
  DiffStats,
  DiffInput,
  DiffToneClasses,
  DiffViewerProps,
} from './types';
