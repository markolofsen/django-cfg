import { describe, expect, it } from "vitest";

import { linkHost, previewable, safeIcon, usableTitle } from "./preview";

describe("previewable", () => {
  it("asks only for https", () => {
    expect(previewable("https://example.com/a")).toBe(true);
    expect(previewable("http://example.com")).toBe(false);
    expect(previewable("mailto:a@b.co")).toBe(false);
    expect(previewable("javascript:alert(1)")).toBe(false);
  });
});

describe("safeIcon", () => {
  it("keeps a plain inline image", () => {
    expect(safeIcon("data:image/png;base64,iVBORw0KGgo=")).toBeDefined();
  });
  it("drops anything that is an address, a script, markup or too large", () => {
    expect(safeIcon(undefined)).toBeUndefined();
    expect(safeIcon("https://evil.example/x.png")).toBeUndefined();
    expect(safeIcon("data:text/html;base64,PHNjcmlwdD4=")).toBeUndefined();
    expect(safeIcon('data:image/png;base64,AAAA"onerror="x')).toBeUndefined();
    expect(safeIcon(`data:image/png;base64,${"A".repeat(40_001)}`)).toBeUndefined();
  });
});

describe("linkHost", () => {
  it("drops www and survives garbage", () => {
    expect(linkHost("https://www.example.com/a?b=1")).toBe("example.com");
    expect(linkHost("not a url")).toBe("");
  });
});

describe("usableTitle", () => {
  it("collapses whitespace, caps length, refuses empty", () => {
    expect(usableTitle({ title: "  A \n  title " })).toBe("A title");
    expect(usableTitle({ title: "x".repeat(300) })?.length).toBe(140);
    expect(usableTitle({ title: "   " })).toBeUndefined();
    expect(usableTitle(undefined)).toBeUndefined();
  });
});
