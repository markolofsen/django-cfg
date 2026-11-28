/**
 * The qualifier an MCP client prepends to every tool it borrows from a server.
 *
 * Tools are declared BARE on the server — it registers `ask_weather`, not
 * `mcp__server__ask_weather`. The prefix is the client's
 * namespacing, so stripping it restores the name we chose rather than inventing
 * a nickname for a name we did not.
 *
 * Lazy on purpose: it must close at the FIRST separator, because `__` is legal
 * inside a tool's own name and a greedy match would eat into it.
 */
const QUALIFIED = /^mcp__.+?__/;

/**
 * The tool name as a reader should see it.
 *
 * Exactly two segments come off — the marker and the server — because `__` is
 * legal INSIDE a tool's own name. Taking the text after the last separator
 * instead would silently shorten any such tool, and nothing would fail: the row
 * still renders, just under half a name.
 *
 * A name that is not qualified passes through untouched, which is what keeps
 * one engine's rows (`ToolSearch`) sitting level with another's in the same
 * transcript.
 */
export function readableToolName(toolName: string): string {
  const bare = toolName.replace(QUALIFIED, "");
  // A name that is ONLY its qualifier leaves nothing to render; the raw string
  // is a worse label than the original, so the original stands.
  return bare === "" ? toolName : bare;
}
