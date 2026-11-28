import { readFileSync } from "node:fs";

import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { MenuRow } from "./mention-menu";
import { MentionMenu, mentionTextareaAria, optionId } from "./mention-menu";

/**
 * The ARIA contract, asserted on both sides.
 *
 * Static markup is enough here and deliberately so: every claim below is about
 * what the ATTRIBUTES say, not about interaction, and a mismatch between the
 * textarea's `aria-activedescendant` and the option's `id` is silent — the
 * markup validates, and only a screen reader user ever finds out.
 */

const CANDIDATES: readonly MenuRow[] = [
  { id: "a", label: "Assistant", hint: "Only the assistant answers" },
  { id: "b", label: "Everyone" },
];

const render = (node: Parameters<typeof renderToStaticMarkup>[0]) =>
  renderToStaticMarkup(node);

describe("the listbox", () => {
  it("is a labelled listbox of options", () => {
    const html = render(
      <MentionMenu
        candidates={CANDIDATES}
        activeIndex={0}
        listboxId="mentions"
        label="Mention"
        onSelect={() => {}}
      />,
    );

    expect(html).toContain('role="listbox"');
    expect(html).toContain('aria-label="Mention"');
    expect(html.match(/role="option"/g) ?? []).toHaveLength(2);
  });

  it("marks exactly one option selected", () => {
    const html = render(
      <MentionMenu
        candidates={CANDIDATES}
        activeIndex={1}
        listboxId="mentions"
        label="Mention"
        onSelect={() => {}}
      />,
    );

    expect(html.match(/aria-selected="true"/g) ?? []).toHaveLength(1);
    expect(html).toContain(`id="${optionId("mentions", 1)}"`);
  });

  it("renders an empty state as presentation, never as an option", () => {
    // Counting it as an option makes a screen reader announce "1 of 1" for a
    // list with no results.
    const html = render(
      <MentionMenu
        candidates={[]}
        activeIndex={0}
        listboxId="mentions"
        label="Mention"
        emptyLabel="No one to mention"
        onSelect={() => {}}
      />,
    );

    expect(html).toContain("No one to mention");
    expect(html).not.toContain('role="option"');
  });

  /**
   * No options ⇒ no listbox. Found by `a11y: { test: "error" }` on the composer
   * stories: axe's `aria-required-children` rejects a `listbox`
   * with no `option` inside it, and the empty-state row cannot become one
   * without making a screen reader announce "1 of 1" for zero results. The
   * element stops claiming to be a list instead.
   */
  it("does not claim to be a listbox when it holds no options", () => {
    const html = render(
      <MentionMenu
        candidates={[]}
        activeIndex={0}
        listboxId="mentions"
        label="Mention"
        emptyLabel="No one to mention"
        onSelect={() => {}}
      />,
    );

    expect(html).not.toContain('role="listbox"');
    expect(html).toContain('role="status"');
    // The id must survive the role change: the textarea's `aria-controls`
    // points at it either way, and a dangling reference is silent.
    expect(html).toContain('id="mentions"');
  });

  it("never emits an empty live region while a search is in flight", () => {
    // `loading` can be true with no `emptyLabel`; an empty <p> inside a status
    // announces nothing at all.
    const html = render(
      <MentionMenu
        candidates={[]}
        activeIndex={0}
        listboxId="mentions"
        label="Mention"
        loading
        onSelect={() => {}}
      />,
    );

    expect(html).not.toContain("<p");
    expect(html).toContain('aria-busy="true"');
  });

  it("renders nothing when there is neither content nor anything to say", () => {
    // An empty box would leave the textarea's `aria-controls` pointing at an
    // element with no meaning.
    const html = render(
      <MentionMenu
        candidates={[]}
        activeIndex={0}
        listboxId="mentions"
        label="Mention"
        onSelect={() => {}}
      />,
    );

    expect(html).toBe("");
  });
});

describe("the textarea's attributes", () => {
  const open = { open: true, listboxId: "mentions", activeIndex: 1, navigated: true };

  it("never claims combobox, which ARIA-in-HTML forbids on a textarea", () => {
    // `role="combobox"` and `aria-expanded` are both rejected by axe on a
    // multiline textarea. The valid pattern is aria-autocomplete + controls +
    // activedescendant, so this asserts the absence as much as the presence.
    const aria = mentionTextareaAria(open);

    expect(aria.role).toBeUndefined();
    expect(aria["aria-expanded"]).toBeUndefined();
    expect(aria["aria-autocomplete"]).toBe("list");
  });

  it("points aria-controls at the listbox whenever open", () => {
    expect(mentionTextareaAria(open)["aria-controls"]).toBe("mentions");
    expect(
      mentionTextareaAria({ ...open, open: false })["aria-controls"],
    ).toBeUndefined();
  });

  it("withholds aria-activedescendant until the user has navigated", () => {
    // Set eagerly, a screen reader re-reads the first option on every keystroke
    // as the list re-filters — the reason this flag exists separately from
    // `activeIndex`.
    expect(
      mentionTextareaAria({ ...open, navigated: false })["aria-activedescendant"],
    ).toBeUndefined();
    expect(mentionTextareaAria(open)["aria-activedescendant"]).toBe("mentions-option-1");
  });

  it("agrees with the rendered option id — the two sides derive, never share", () => {
    // THE ASSERTION THAT MATTERS. A mismatch here is invisible: valid markup,
    // no error, and a screen reader that announces nothing on navigation.
    const html = render(
      <MentionMenu
        candidates={CANDIDATES}
        activeIndex={1}
        listboxId="mentions"
        label="Mention"
        onSelect={() => {}}
      />,
    );

    const active = mentionTextareaAria(open)["aria-activedescendant"];
    expect(active).toBeDefined();
    expect(html).toContain(`id="${active}"`);
  });
});

describe("selection uses mousedown, not click", () => {
  it("is documented in the source, because the markup cannot show it", () => {
    // A click blurs the textarea first, which closes the menu and moves the
    // caret — so the selection lands in a composer that already changed. Static
    // markup carries no handlers, so this is a source assertion, named as one.
    const source = new URL("./mention-menu.tsx", import.meta.url).pathname;
    // Comments stripped FIRST. The source explains why `onClick` is wrong, so
    // matching raw text finds the word in the explanation and fails on the very
    // comment that documents compliance — the same trap the a11y ratchet hit,
    // and the reason `@rules/testing.md` names it.
    const code = readFileSync(source, "utf8")
      .replace(/\/\*[\s\S]*?\*\//g, "")
      .replace(/\/\/.*$/gm, "");

    expect(code).toContain("onMouseDown");
    expect(code).not.toContain("onClick");
  });
});
