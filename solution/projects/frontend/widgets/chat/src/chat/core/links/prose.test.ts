import { describe, expect, it } from "vitest";

import { isBareUrlLink, isExternalHref, linkChipLabel, splitUrl } from "./prose";

/**
 * The answer that produced the defect: eight deep links into ONE domain. The
 * donor `truncateUrlLabel` collapsed five of them to a bare `docs.widget.io/…`,
 * so the message rendered eight identical labels. That is the case these
 * assertions exist to hold.
 */
const DOCS_ANSWER = [
  "https://docs.widget.io/cli/daemon/service#install-options",
  "https://docs.widget.io/cli/remote/authentication#join-and-start-a-session",
  "https://docs.widget.io/cli/install#windows",
  "https://docs.widget.io/cli/install#download-the-binary-directly",
  "https://docs.widget.io/cli/daemon#agent-and-service",
  "https://docs.widget.io/docs/mcp/claude-desktop#remove-the-registration",
  "https://docs.widget.io/guides/ai-agent/teams#5-remove-access-when-finished",
  "https://docs.widget.io/docs/install#install-guide",
] as const;

const ELLIPSIS = "…";

describe("linkChipLabel", () => {
  it("keeps eight links into one domain distinguishable", () => {
    const labels = DOCS_ANSWER.map((url) => linkChipLabel(url));
    expect(new Set(labels).size).toBe(labels.length);
  });

  it("never falls back to a bare domain", () => {
    for (const url of DOCS_ANSWER) {
      expect(linkChipLabel(url)).not.toBe(`docs.widget.io/${ELLIPSIS}`);
    }
  });

  it("stays within the budget", () => {
    for (const url of DOCS_ANSWER) {
      expect(linkChipLabel(url).length).toBeLessThanOrEqual(40);
    }
  });

  it("sheds the hash before a path segment", () => {
    expect(linkChipLabel("https://docs.widget.io/cli/remote/authentication#join-and-start-a-session")).toBe(
      "docs.widget.io/cli/remote/authentication",
    );
    expect(linkChipLabel("https://docs.widget.io/guides/ai-agent/teams#5-remove-access-when-finished")).toBe(
      "docs.widget.io/guides/ai-agent/teams",
    );
    // The discriminating pair: a whole path with no fragment beats an elided
    // path carrying one. Grouping every hash-bearing candidate ahead of every
    // bare one passes the two above and returns `…/service#install-options`
    // here, which names the page less well than the segments do.
    expect(linkChipLabel("https://docs.widget.io/cli/daemon/service#install-options")).toBe(
      "docs.widget.io/cli/daemon/service",
    );
    expect(linkChipLabel("https://docs.widget.io/docs/install#install-guide")).toBe(
      "docs.widget.io/docs/install",
    );
  });

  it("keeps a hash that fits", () => {
    expect(linkChipLabel("https://docs.widget.io/cli/install#windows")).toBe(
      "docs.widget.io/cli/install#windows",
    );
  });

  it("puts the elision where the gap is", () => {
    // Middle dropped: the mark sits between the two survivors.
    expect(linkChipLabel("https://github.com/wailsapp/wails/blob/main/v3/README.md")).toBe(
      "github.com/wailsapp/…/README.md",
    );
    // Everything before the last dropped: the mark LEADS. `last/…` would point
    // the reader at the wrong end of the path.
    expect(linkChipLabel("https://example.com/one/two/three/a-very-long-final-segment")).toBe(
      "example.com/…/a-very-long-final-segment",
    );
  });

  it("leaves a short url alone", () => {
    expect(linkChipLabel("https://github.com/wailsapp/wails")).toBe("github.com/wailsapp/wails");
    expect(linkChipLabel("https://example.com")).toBe("example.com");
    expect(linkChipLabel("https://www.example.com/a")).toBe("example.com/a");
  });

  it("shows a mail address without the scheme", () => {
    expect(linkChipLabel("mailto:hi@widget.io")).toBe("hi@widget.io");
  });

  it("keeps the page name when the last segment alone overruns", () => {
    const label = linkChipLabel("https://example.com/averyveryverylongsinglesegmentnamehere");
    expect(label.startsWith("example.com/a")).toBe(true);
    expect(label.endsWith(ELLIPSIS)).toBe(true);
  });

  /**
   * The CONTROL, and the reason it is not a list of expected strings: a label
   * whose `…` stands for nothing looks entirely correct in a snapshot. This
   * compares the number of segments the label NAMES against the number the url
   * HAS — an `…` requires that more were dropped, and its absence requires that
   * none were.
   *
   * It runs over a url with no elision at all, so it can fail in both
   * directions rather than only catching a missing mark.
   */
  it("only claims an elision when segments actually fell", () => {
    const cases = [
      ...DOCS_ANSWER,
      "https://github.com/wailsapp/wails/blob/main/v3/README.md",
      "https://github.com/wailsapp/wails",
      "https://example.com",
      // Six segments plus a fragment, and the whole thing fits: an elision
      // mark here would be the lie, so this is the direction a control that
      // only looked for missing marks could never catch.
      "https://example.com/a/b/c/d/e/f#x",
    ];
    for (const url of cases) {
      const label = linkChipLabel(url);
      const real = splitUrl(url).segments.length;
      const body = label.replace(/#.*$/, "");
      const parts = body.split("/").slice(1);
      const named = parts.filter((p) => p !== ELLIPSIS).length;
      if (parts.includes(ELLIPSIS)) {
        expect(real, `${url} → ${label}`).toBeGreaterThan(named);
      } else {
        expect(real, `${url} → ${label}`).toBe(named);
      }
    }
  });
});

describe("isBareUrlLink", () => {
  const url = "https://docs.widget.io/cli/install";

  it("claims a url whose label is the url", () => {
    expect(isBareUrlLink(url, url)).toBe(true);
  });

  it("declines a label the author wrote", () => {
    expect(isBareUrlLink(url, "the docs")).toBe(false);
  });

  it("declines a formatted label, which has no lone text child", () => {
    expect(isBareUrlLink(url, undefined)).toBe(false);
  });

  it("claims a schemeless www host", () => {
    // gfm rewrites the url and leaves the text alone, so a raw equality would
    // miss the exact shape a model writes when it elides the scheme.
    expect(isBareUrlLink("http://www.widget.io", "www.widget.io")).toBe(true);
  });

  it("declines a mail autolink", () => {
    expect(isBareUrlLink("mailto:hi@widget.io", "hi@widget.io")).toBe(false);
  });

  it("declines an app scheme, whose href never equals its label", () => {
    expect(isBareUrlLink("app://note/n1", "@notes")).toBe(false);
  });
});

describe("isExternalHref", () => {
  it("accepts the web schemes a new tab makes sense for", () => {
    expect(isExternalHref("https://a.com")).toBe(true);
    expect(isExternalHref("mailto:hi@widget.io")).toBe(true);
  });

  it("rejects an app scheme, which would spawn a blank tab", () => {
    expect(isExternalHref("app://note/n1")).toBe(false);
    expect(isExternalHref(undefined)).toBe(false);
  });
});
