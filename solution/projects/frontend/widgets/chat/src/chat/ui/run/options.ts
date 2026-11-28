import type { RunPrivacyOptions } from "../../core/run/privacy";

/**
 * What a host passes to `createRunRenderer`. Everything is optional; the defaults
 * show a step's phrase and its one-line summary, the argument NAMES and a short
 * result preview (behind the step's own disclosure), and no words of a thought.
 */
export interface RunOptions extends RunPrivacyOptions {
  /** A title per tool name, ahead of the server's own label: `{ kb_search: "Searching the knowledge base" }`. */
  readonly labels?: Readonly<Record<string, string>>;
  /** Start expanded. Default: collapsed, except that a run with a failed step opens itself. */
  readonly defaultOpen?: boolean;
  /** Show the copy button. Default true. It carries exactly what the screen shows. */
  readonly allowCopy?: boolean;
}
