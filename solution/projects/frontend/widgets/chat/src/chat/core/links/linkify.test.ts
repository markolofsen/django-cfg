import { describe, expect, it } from "vitest";

import { findLinks, linkLabel, opensInNewTab, safeHref } from "./linkify";
import { mentionSpans } from "../room/recipient";

const NOTION =
  "https://app.notion.com/p/bridgetowncompanies/352004e89e0a80cb8a1fc1e3a7a96d4f?source=copy_link&p=1a2b3c&pm=s";

describe("safeHref", () => {
  it("lets web and mail through", () => {
    expect(safeHref("https://example.com/a")).toBe("https://example.com/a");
    expect(safeHref("http://example.com")).toBe("http://example.com");
    expect(safeHref("mailto:a@example.com")).toBe("mailto:a@example.com");
    expect(safeHref("www.example.com/x")).toBe("https://www.example.com/x");
  });

  it("refuses every other scheme", () => {
    for (const bad of ["javascript:alert(1)", "data:text/html,x", "file:///etc/passwd", "app://tool/x", "tel:+1555", "vbscript:x", "JaVaScRiPt:alert(1)"]) {
      expect(safeHref(bad)).toBeUndefined();
    }
  });

  it("refuses userinfo, whitespace, control characters and hostless input", () => {
    expect(safeHref("https://google.com@evil.test/")).toBeUndefined();
    expect(safeHref("https://exa mple.com")).toBeUndefined();
    expect(safeHref("https://example.com/\u0000")).toBeUndefined();
    expect(safeHref("https://intranet")).toBeUndefined();
    expect(safeHref("mailto:")).toBeUndefined();
    expect(safeHref(undefined)).toBeUndefined();
  });
});

describe("findLinks", () => {
  it("finds the whole long address", () => {
    const text = `see ${NOTION} please`;
    const [link] = findLinks(text);
    expect(link?.href).toBe(NOTION);
    expect(text.slice(link!.start, link!.end)).toBe(NOTION);
  });

  it("leaves sentence punctuation out of the link", () => {
    const [a] = findLinks("go to https://example.com/a.");
    expect(a?.href).toBe("https://example.com/a");
    const [b] = findLinks("(see https://example.com/a), ok");
    expect(b?.href).toBe("https://example.com/a");
    const [c] = findLinks("really https://example.com/a?!");
    expect(c?.href).toBe("https://example.com/a");
  });

  it("keeps a bracket the url opened", () => {
    const [link] = findLinks("https://en.wikipedia.org/wiki/Foo_(bar)");
    expect(link?.href).toBe("https://en.wikipedia.org/wiki/Foo_(bar)");
  });

  it("finds several, and www hosts", () => {
    const links = findLinks("https://a.example/x and www.b.example/y");
    expect(links.map((l) => l.href)).toEqual(["https://a.example/x", "https://www.b.example/y"]);
  });

  it("ignores an unsafe scheme and a scheme glued to a word", () => {
    expect(findLinks("javascript:alert(1) and xhttps://a.example")).toEqual([]);
  });

  it("does not turn an @-mention into a link or cut one in two", () => {
    const items = [{ id: "anna", label: "Anna", seat: "s1" }];
    const text = "@Anna look at https://example.com/@Anna and @Anna again";
    const spans = mentionSpans(text, items);
    const links = findLinks(text, spans);
    expect(spans.length).toBe(2);
    // The url keeps its own `@Anna`: mentions need whitespace before them.
    expect(links).toHaveLength(1);
    expect(links[0]?.href).toBe("https://example.com/@Anna");
    for (const link of links) {
      for (const span of spans) expect(link.start < span.end && link.end > span.start).toBe(false);
    }
  });

  it("drops a link that overlaps a skipped range", () => {
    expect(findLinks("https://example.com/a", [{ start: 3, end: 8 }])).toEqual([]);
  });
});

describe("linkLabel", () => {
  it("shortens the notion address to host plus the page's name, query dropped", () => {
    const label = linkLabel(NOTION);
    expect(label.startsWith("app.notion.com/")).toBe(true);
    expect(label.length).toBeLessThanOrEqual(41);
    expect(label).not.toContain("source=");
    expect(label.endsWith("…")).toBe(true);
  });

  it("leaves a short address alone", () => {
    expect(linkLabel("https://example.com/a")).toBe("example.com/a");
  });

  it("marks a dropped query even when the rest fits", () => {
    expect(linkLabel("https://example.com/a?x=1")).toBe("example.com/a…");
  });

  it("shows a mail address as is", () => {
    expect(linkLabel("mailto:a@example.com")).toBe("a@example.com");
  });
});

describe("opensInNewTab", () => {
  it("is for web pages only", () => {
    expect(opensInNewTab("https://example.com")).toBe(true);
    expect(opensInNewTab("mailto:a@example.com")).toBe(false);
  });
});
