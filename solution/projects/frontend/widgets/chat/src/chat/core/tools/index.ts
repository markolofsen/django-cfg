// The tool arsenal: what this agent can do here, as data.
//
// Pure by design — the catalogue arrives from the host (Go owns the registry),
// and the surface rendering it is meant to be swappable. May import: nothing.

export type { ToolsCapability } from "./capability";
export {
  filterToolCatalogue,
  groupToolsByCategory,
  toolMatchesQuery,
  type ToolCatalogEntry,
  type ToolCatalogGroup,
} from "./menu/catalogue";
export { queryLayoutForms } from "./menu/layout";
export { nextRow, stepForKey, NO_ROW } from "./menu/nav";
export { scoreTool } from "./menu/rank";
export { forgetTool, recentTools, rememberTool, RECENT_LIMIT } from "./menu/recent";
