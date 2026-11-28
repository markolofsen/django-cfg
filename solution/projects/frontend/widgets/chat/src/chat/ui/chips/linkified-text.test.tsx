import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { LinkifiedText } from "./linkified-text";

const URL_LONG = "https://app.notion.com/p/bridgetowncompanies/352004e89e0a80cb8a1fc1e3a7a96d4f?source=copy_link&p=1&pm=s";

describe("LinkifiedText", () => {
  it("returns plain text untouched", () => {
    expect(renderToStaticMarkup(<LinkifiedText text="no links here" />)).toBe("no links here");
  });

  it("draws a long address as a short, safe, clickable chip with the copy control", () => {
    const html = renderToStaticMarkup(<LinkifiedText text={`see ${URL_LONG} ok`} />);
    expect(html).toContain("see ");
    expect(html).toContain(" ok");
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noopener noreferrer"');
    expect(html).toContain("chat-link-copy");
    expect(html).not.toContain(`>${URL_LONG}<`);
  });

  it("never links the skipped range", () => {
    const html = renderToStaticMarkup(<LinkifiedText text="https://example.com/a" skip={[{ start: 0, end: 5 }]} />);
    expect(html).not.toContain("<a ");
  });

  it("does not link an unsafe scheme", () => {
    expect(renderToStaticMarkup(<LinkifiedText text="javascript:alert(1)" />)).not.toContain("<a ");
  });
});
