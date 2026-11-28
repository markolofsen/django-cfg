import { describe, expect, it } from "vitest";

import { contextHash, readPageContext, type PageSource } from "./context";

/** A payload carrying just the field this module reads. */
const payload = (hash: string) => ({ metadata: { contentHash: hash } }) as never;

const source = (hash: string | null): PageSource => ({
  getChatMetadata: () => (hash === null ? undefined : { pageContext: payload(hash) }),
  isStale: false,
});

describe("readPageContext", () => {
  it("sends the full page on the first turn", () => {
    const context = readPageContext(source("aaaa1111"), null);
    expect(context?.kind).toBe("snapshot");
  });

  /**
   * The measured reason the content hash exists. A tree is thousands of
   * tokens; an unchanged page re-stated as a hash is one line, and the refs
   * the agent already holds still resolve because nothing moved.
   */
  it("sends a reference when the page has not changed", () => {
    const context = readPageContext(source("aaaa1111"), "aaaa1111");
    expect(context).toEqual({ kind: "unchanged", hash: "aaaa1111" });
  });

  it("sends the full page again once it changes", () => {
    const context = readPageContext(source("bbbb2222"), "aaaa1111");
    expect(context?.kind).toBe("snapshot");
  });

  it("sends nothing when the user has not opted in", () => {
    expect(readPageContext(source(null), null)).toBeUndefined();
  });

  /**
   * `getChatMetadata` is typed as an open record, so a host wiring a different
   * contributor into the same seam reaches this branch rather than sending a
   * context with no payload.
   */
  it("sends nothing when the metadata carries no page", () => {
    const odd: PageSource = { getChatMetadata: () => ({}), isStale: false };
    expect(readPageContext(odd, null)).toBeUndefined();
  });
});

describe("contextHash", () => {
  it("reads the hash out of either shape", () => {
    expect(contextHash({ kind: "unchanged", hash: "cccc3333" })).toBe("cccc3333");
    expect(contextHash({ kind: "snapshot", payload: payload("dddd4444") })).toBe("dddd4444");
  });
});
