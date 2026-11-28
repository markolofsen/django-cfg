/**
 * The ONE code block: Prism via `prism-react-renderer`, a header with the
 * language and a copy button, the `--code*` surface tokens, a compact mode.
 *
 * Eager. A host that wants the highlighter in its own chunk imports
 * `./lazy` instead. Not re-exported from the package root: the root is pure,
 * and this pulls React, `ui-core` and Prism.
 */
export { PrettyCode } from './pretty-code';
export type { PrettyCodeProps, PrettyCodeLabels } from './pretty-code';
export { CodePanelHeader } from './code-panel-header';
export type { CodePanelHeaderProps } from './code-panel-header';
export { languageLabel, normalizePrismLanguage } from './languages';
export { ensurePrismLanguages, useEnsurePrismLanguages } from './prism-languages';
export type { Language } from 'prism-react-renderer';
