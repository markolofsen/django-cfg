import { describe, expect, it } from "vitest";
import { cleanPath, isAllowedSrc } from "./allowed-src";

/**
 * A security gate, so the tests are written as ATTACKS rather than as examples.
 *
 * Mirrored from the server's own allowlist. Every rejection case below
 * corresponds to a bypass that implementation calls out by name; if the two
 * ever disagree, one of them is a vulnerability.
 */

const PREFIXES = ["/api/admin/", "/media/"] as const;
const allowed = (src: string) => isAllowedSrc(src, PREFIXES);

describe("schemes", () => {
  it("accepts the four the server accepts", () => {
    expect(allowed("https://example.com/a.png")).toBe(true);
    expect(allowed("app://note/file.png")).toBe(true);
    expect(allowed("data:image/png;base64,AAAA")).toBe(true);
    expect(allowed("/api/admin/files/1.png")).toBe(true);
  });

  it("rejects script-bearing and origin-crossing schemes", () => {
    // `javascript:` is the obvious one; `data:text/html` is the one that looks
    // like the allowed `data:` case and is script all the same.
    expect(allowed("javascript:alert(1)")).toBe(false);
    expect(allowed("data:text/html,<script>alert(1)</script>")).toBe(false);
    expect(allowed("vbscript:msgbox")).toBe(false);
    // Plain http downgrades the transport and leaks the request in clear text.
    expect(allowed("http://example.com/a.png")).toBe(false);
    expect(allowed("file:///etc/passwd")).toBe(false);
  });

  it("is case-insensitive about the scheme, since the browser is", () => {
    // A gate that only matches lowercase is bypassed by typing `JavaScript:`.
    expect(allowed("HTTPS://example.com/a.png")).toBe(true);
    expect(allowed("JaVaScRiPt:alert(1)")).toBe(false);
    expect(allowed("DATA:IMAGE/PNG;base64,AA")).toBe(true);
  });

  it("rejects empty and whitespace-only", () => {
    expect(allowed("")).toBe(false);
    expect(allowed("   ")).toBe(false);
  });
});

describe("same-origin paths", () => {
  it("accepts an allowlisted prefix", () => {
    expect(allowed("/api/admin/x.png")).toBe(true);
    expect(allowed("/media/y.png")).toBe(true);
  });

  it("rejects a path outside every prefix", () => {
    expect(allowed("/etc/passwd")).toBe(false);
    expect(allowed("/api/other/x")).toBe(false);
  });

  it("rejects the two protocol-relative escapes by name", () => {
    // `//evil.com/x` is a full URL to another origin. `/\evil.com` is treated
    // as one by some browsers — which is why matching a `/` prefix alone is
    // not enough, and why both are named in the gate's comment.
    expect(allowed("//evil.com/x.png")).toBe(false);
    expect(allowed("/\\evil.com/x.png")).toBe(false);
  });

  it("rejects traversal instead of normalising it away", () => {
    // THE RULE: reject, do not clean. Cleaning first and then matching is how
    // `/api/admin/../../etc/passwd` becomes an allowed `/etc/passwd`.
    expect(allowed("/api/admin/../../etc/passwd")).toBe(false);
    expect(allowed("/api/admin/./x.png")).toBe(false);
    expect(allowed("/api/admin//x.png")).toBe(false);
  });

  it("allows a query or fragment after a clean path", () => {
    // The gate applies to the path portion only — `?path=…` is legitimate.
    expect(allowed("/api/admin/x.png?v=2")).toBe(true);
    expect(allowed("/media/y.png#frag")).toBe(true);
    // …but the path is still checked, so traversal before the query fails.
    expect(allowed("/api/admin/../x.png?v=2")).toBe(false);
  });
});

describe("cleanPath matches Go's path.Clean on the cases that decide the gate", () => {
  it("collapses the segments Go collapses", () => {
    expect(cleanPath("/a/b/../c")).toBe("/a/c");
    expect(cleanPath("/a//b")).toBe("/a/b");
    expect(cleanPath("/a/./b")).toBe("/a/b");
    expect(cleanPath("/a/b/")).toBe("/a/b");
  });

  it("drops `..` at the root, where Go has nowhere to go", () => {
    expect(cleanPath("/..")).toBe("/");
    expect(cleanPath("/../..")).toBe("/");
  });

  it("leaves an already-clean path untouched", () => {
    // The gate is `path !== cleanPath(path)`, so a false positive here would
    // reject legitimate media rather than admit an attack — still a defect.
    expect(cleanPath("/api/admin/x.png")).toBe("/api/admin/x.png");
    expect(cleanPath("/")).toBe("/");
  });
});

describe("the control", () => {
  it("can return true at all, so the rejections above are not vacuous", () => {
    // Every attack case asserts `false`. If the function returned false for
    // everything — a thrown-and-caught error, an inverted condition — the whole
    // suite would pass while blocking all media.
    expect(allowed("https://example.com/a.png")).toBe(true);
  });

  it("respects the prefixes it is GIVEN, not a baked-in list", () => {
    // The prefix list belongs to the host. Passing an empty list must reject
    // every path; if it did not, the parameter would be decorative.
    expect(isAllowedSrc("/api/admin/x.png", [])).toBe(false);
    expect(isAllowedSrc("/custom/x.png", ["/custom/"])).toBe(true);
  });
});
