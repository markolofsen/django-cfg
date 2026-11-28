/**
 * One row. Structural rather than `MentionItem`, so the listbox stays about how
 * a listbox behaves and not about what a room can name.
 *
 * Restored from django-cfg `981754ced^`, where it also listed `/`-commands and
 * drew a face before the label; neither is needed here.
 */
export interface MenuRow {
  readonly id: string;
  readonly label: string;
  readonly hint?: string;
}

/**
 * The mention menu surface.
 *
 * ## The ARIA pattern, and why NOT combobox
 *
 * Taken from `@sources/stream-chat-react`, which states the constraint
 * outright: **`role="combobox"` is disallowed on a multiline `<textarea>`** by
 * ARIA-in-HTML, and `aria-expanded` is not supported on the implicit `textbox`
 * role — axe rejects both. The valid pattern on a textbox is:
 *
 * ```text
 * textarea:  aria-autocomplete="list"
 *            aria-controls          → the listbox id   (whenever open)
 *            aria-activedescendant  → the active option (ONLY after navigation)
 * listbox:   role="listbox"   + an aria-label
 * option:    role="option"    + aria-selected + a derived id
 * ```
 *
 * The `aria-activedescendant` timing is the subtle half, and also theirs: set
 * unconditionally, a screen reader re-reads the first option on every keystroke
 * as the list re-filters. It is announced only once the user has actually
 * navigated — which is why `activeIndex` alone is not enough to drive it.
 *
 * Focus never leaves the textarea. That is the whole point of this pattern over
 * a roving-tabindex list: the user is still typing.
 */

export interface MentionMenuProps<Row extends MenuRow = MenuRow> {
  readonly candidates: readonly Row[];
  readonly activeIndex: number;
  /** Shared with the textarea's `aria-controls`, and the source of option ids. */
  readonly listboxId: string;
  /** The accessible name. Host copy — this package carries no locales. */
  readonly label: string;
  readonly onSelect: (candidate: Row) => void;
  readonly loading?: boolean;
  /** Rendered when a search returned nothing. Absent ⇒ the menu hides instead. */
  readonly emptyLabel?: string;
  readonly className?: string;
}

/** Option id derived from the listbox id — the textarea builds the same string. */
export function optionId(listboxId: string, index: number): string {
  return `${listboxId}-option-${index}`;
}

export function MentionMenu<Row extends MenuRow>({
  candidates,
  activeIndex,
  listboxId,
  label,
  onSelect,
  loading = false,
  emptyLabel,
  className,
}: MentionMenuProps<Row>) {
  // Nothing to show and nothing to say: render no element at all rather than an
  // empty box, so `aria-controls` on the textarea points at something real.
  if (candidates.length === 0 && !loading && emptyLabel === undefined) return null;

  /**
   * No options ⇒ NO LISTBOX. The status message keeps the same id instead.
   *
   * `role="listbox"` is required to contain `option` children
   * (axe `aria-required-children`), and an empty-state row cannot be one: a
   * selectable "No matches" makes a screen reader announce "1 of 1" for a list
   * with no results, and Enter on it commits nothing. Both facts are true, so
   * the element itself has to stop claiming to be a list.
   *
   * Caught by `a11y: { test: "error" }` on the stories — the markup
   * validates as far as every other assertion can see.
   *
   * `stream-chat-react`, which this whole ARIA pattern comes from, never
   * reaches the state at all: its list opens only on `items?.length`, so an
   * empty listbox cannot exist. We do render something — a search that returned
   * nothing is worth saying — so it is a `status` instead, which announces
   * politely and owns `listboxId` so the textarea's `aria-controls` still
   * points at a real element.
   */
  if (candidates.length === 0) {
    return (
      <div
        id={listboxId}
        role="status"
        aria-label={label}
        aria-busy={loading || undefined}
        className={className}
        data-slot="mention-menu"
      >
        {/*
          `emptyLabel` can be absent while `loading` is true — the guard above
          only returns null when BOTH are absent. Rendering the paragraph
          unconditionally would emit an empty `<p>` inside a live region, which
          announces nothing and reads as a bug to a screen reader user.
        */}
        {emptyLabel === undefined ? null : (
          <p className="px-2 py-1.5 text-sm text-muted-foreground">{emptyLabel}</p>
        )}
      </div>
    );
  }

  return (
    <ul
      id={listboxId}
      role="listbox"
      aria-label={label}
      aria-busy={loading || undefined}
      className={className}
      data-slot="mention-menu"
    >
      {candidates.map((candidate, index) => (
        <li
          key={candidate.id}
          id={optionId(listboxId, index)}
          role="option"
          aria-selected={index === activeIndex}
          // `onMouseDown` with preventDefault, NOT `onClick`: a click would
          // blur the textarea first, which closes the menu and moves the caret
          // — so the selection would land in a composer that already changed
          // underneath it.
          onMouseDown={(event) => {
            event.preventDefault();
            onSelect(candidate);
          }}
          className={`flex cursor-pointer items-center gap-2 px-2 py-1.5 text-sm ${
            index === activeIndex ? "bg-accent text-accent-foreground" : ""
          }`}
        >
          <span className="truncate">{candidate.label}</span>
          {candidate.hint === undefined ? null : (
            <span className="truncate text-xs text-muted-foreground">{candidate.hint}</span>
          )}
        </li>
      ))}
    </ul>
  );
}

/**
 * The ARIA attributes the TEXTAREA must carry while a menu is open.
 *
 * A function rather than prose in a comment, because the two sides have to
 * agree on ids that are derived, not passed — and a mismatch is silent: the
 * markup validates, and only a screen reader user finds out.
 */
export function mentionTextareaAria(options: {
  readonly open: boolean;
  readonly listboxId: string;
  readonly activeIndex: number;
  /** True once the user has moved the highlight with the keyboard. */
  readonly navigated: boolean;
}): Record<string, string | undefined> {
  const { open, listboxId, activeIndex, navigated } = options;

  return {
    // Always present: it describes the field's behaviour, not the menu's state.
    "aria-autocomplete": "list",
    // Discoverable whenever the list is open.
    "aria-controls": open ? listboxId : undefined,
    // ONLY after navigation. Set eagerly, a screen reader re-reads the first
    // option on every keystroke as the list re-filters.
    "aria-activedescendant":
      open && navigated ? optionId(listboxId, activeIndex) : undefined,
  };
}
