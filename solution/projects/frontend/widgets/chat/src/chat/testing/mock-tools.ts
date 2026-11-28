import type { ToolCatalogEntry } from "../core";

/**
 * A stand-in arsenal, shaped like the registry's projection.
 *
 * Ids, categories and keywords are shaped like the ones a server actually
 * reports, so the filter is exercised against realistic strings rather than
 * against the words a test author would have picked.
 */
export const MOCK_TOOL_CATALOGUE: readonly ToolCatalogEntry[] = [
  {
    id: "transcribe_audio",
    name: "Transcribe audio",
    summary: "Read back what was said in a recording",
    category: "stt",
    keywords: ["stt", "speech", "transcribe", "audio", "voice", "recording", "listen", "said"],
    icon: "mic",
    // The one entry here that wants an object a sentence cannot carry, so the
    // placeholder hint has something real to fire on.
    needs: "file",
  },
  {
    id: "read_text",
    name: "Read an image",
    summary: "Pull the text out of a screenshot or a scan",
    category: "image",
    keywords: ["ocr", "screenshot", "scan", "read"],
    icon: "image",
  },
  {
    id: "web_search",
    name: "Search the web",
    summary: "Look something up online",
    category: "web",
    keywords: ["search", "google", "lookup", "internet"],
    icon: "globe",
  },
  {
    id: "web_fetch",
    name: "Open a page",
    summary: "Fetch one URL and read it",
    category: "web",
    keywords: ["fetch", "url", "page", "browse"],
    icon: "globe",
  },
  {
    id: "read_document",
    name: "Read a document",
    summary: "Open an uploaded document and quote it",
    category: "documents",
    keywords: ["file", "open", "document", "text"],
    icon: "file",
  },
  {
    id: "write_document",
    name: "Write a document",
    summary: "Draft a new document from this conversation",
    category: "documents",
    keywords: ["file", "save", "create", "edit"],
    icon: "file",
  },
  {
    id: "list_documents",
    name: "List documents",
    summary: "See what has been uploaded to this conversation",
    category: "documents",
    keywords: ["ls", "library", "folder", "browse"],
    icon: "file",
  },
  {
    id: "generate_image",
    name: "Generate an image",
    summary: "Draw a picture from a description",
    category: "generation",
    keywords: ["draw", "picture", "render", "illustrate"],
    icon: "image",
  },
  {
    id: "run_code",
    name: "Run code",
    summary: "Execute a snippet in a sandbox and report what it printed",
    category: "code",
    keywords: ["python", "sandbox", "execute", "script"],
    icon: "terminal",
  },
  {
    id: "sandbox_info",
    name: "Sandbox details",
    summary: "Report the runtime and which packages are installed",
    category: "code",
    keywords: ["runtime", "system", "packages", "versions"],
    icon: "terminal",
  },
];

/**
 * The arsenal without speech, as a server with no STT engine reports it.
 * Registration is conditional, so the catalogue differs per deployment.
 */
export const MOCK_TOOL_CATALOGUE_NO_STT: readonly ToolCatalogEntry[] =
  MOCK_TOOL_CATALOGUE.filter((entry) => entry.category !== "stt");
