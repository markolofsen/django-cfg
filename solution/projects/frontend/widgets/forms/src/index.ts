/**
 * Input surfaces: the things a user fills in, picks from or speaks into.
 *
 * No root barrel worth importing — `JsonForm` carries RJSF and `Uploader`
 * carries Rpldy, and neither belongs in an app that only wanted a combobox.
 * Import a subpath.
 */
export type { ComposerHandle } from './composer-registry';
