import { describe, expect, it } from "vitest";

import { readableToolName } from "./name";

describe("readableToolName", () => {
  it("strips the client's qualifier from our own tools", () => {
    expect(readableToolName("mcp__server__ask_weather")).toBe("ask_weather");
    expect(readableToolName("mcp__server__list_cities")).toBe("list_cities");
  });

  it("keeps a server name that contains a single underscore", () => {
    expect(readableToolName("mcp__server_django__crm_list_tasks")).toBe("crm_list_tasks");
  });

  it("leaves an unqualified name alone", () => {
    // The two forms share a transcript: one engine's rows must not be trimmed
    // into a different shape from another's.
    expect(readableToolName("ToolSearch")).toBe("ToolSearch");
    expect(readableToolName("read_file")).toBe("read_file");
  });

  /*
    The control that separates this rule from "take the text after the last
    separator". A tool whose own name carries `__` is shortened by that reading
    and by no other, and the row still renders — so only an assertion sees it.
  */
  it("keeps a separator that belongs to the tool's own name", () => {
    expect(readableToolName("mcp__server__browser__navigate")).toBe("browser__navigate");
  });

  it("declines to strip when nothing would be left", () => {
    expect(readableToolName("mcp__server__")).toBe("mcp__server__");
  });

  it("requires a server name between the separators", () => {
    expect(readableToolName("mcp____tool")).toBe("mcp____tool");
  });

  it("ignores a name that merely starts with the marker", () => {
    expect(readableToolName("mcp_thing")).toBe("mcp_thing");
    expect(readableToolName("mcpx__server__tool")).toBe("mcpx__server__tool");
  });
});
