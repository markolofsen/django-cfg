/**
 * Editor-side slash command info.
 *
 * Deliberately tiny and owned here: the editor's slash menu needs a verb and a
 * token, nothing more. It was once described as a structural subset of the chat
 * package's `SlashCommand` — that type is gone (the chat dropped slash commands
 * when it was generalised for web), and the shape stands on its own.
 */
export interface SlashCommandInfo {
  /** Verb without the leading slash (e.g. `"clear"`). */
  id: string;
  /** Display token with the slash (e.g. `"/clear"`). */
  token: string;
}
