/** Strings of the locale hint. English is the schema of record; `{{language}}` is the target language's own name. */
export interface LocaleSuggestionCopy {
  /** "This page is available in {{language}}" */
  title: string;
  /** Primary button: "Switch to {{language}}" */
  switch: string;
  /** Accessible name of the close button. */
  dismiss: string;
}
