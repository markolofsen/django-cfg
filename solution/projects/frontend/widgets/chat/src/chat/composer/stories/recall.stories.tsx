import type { Meta, StoryObj } from "@storybook/react-vite";

import { tokenize } from "../../testing";
import { ComposerHarness } from "./harness";

/**
 * ↑/↓ prompt recall — walking back through what you already sent.
 *
 * Every rule here is a PORT, not a design: `core/compose/recall/boundary.ts` carries
 * zsh's `up-line-or-beginning-search` test and the typed-buffer rule, and
 * `core/compose/recall/ladder.ts` is the state machine they walk. Both
 * are pure and tested without a DOM (24 assertions); these stories exist for the
 * part an assertion cannot reach — whether an arrow key, a live caret and a
 * textarea agree.
 *
 * The ladder GROWS here as you send, rather than being a fixed fixture. That is
 * deliberate: a story over canned data cannot show the most likely bug, which is
 * a sent prompt never reaching the ladder at all.
 */
const meta = {
  title: "Widgets/Chat/Composer/Recall",
  component: ComposerHarness,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof ComposerHarness>;

export default meta;
type Story = StoryObj<typeof meta>;

const history = [
  "check the server log",
  "restart the agent",
  "show me what changed in core/server",
];

/**
 * The ladder, from an empty composer.
 *
 * Press ↑ repeatedly: the newest prompt first, then older ones, stopping at the
 * oldest rather than wrapping — a ladder that wraps is an infinite loop with no
 * end to feel. Press ↓ to come back down.
 *
 * The caret lands at the END of a recalled entry, because the next thing a user
 * does is edit or resend it; a caret at position 0 would put every keystroke in
 * front of the text they just recalled.
 */
export const WalkTheLadder: Story = {
  args: { history },
};

/**
 * Your own draft comes back.
 *
 * Type something, press ↑ a few times, then ↓ back to the bottom: the text you
 * were writing is restored. It is stashed ONCE, on the first step off the draft —
 * stashing on every step would overwrite it with a recalled entry and the draft
 * would be gone with no error and no way back.
 *
 * Note what ELSE happens: after typing, ↑ does nothing at all until the buffer is
 * empty again. That is the next story.
 */
export const DraftSurvivesTheWalk: Story = {
  args: { history },
};

/**
 * A typed buffer never navigates: once the user has typed a message of their
 * own into the input, recall must not page through history at all.
 *
 * The field is seeded, so ↑ here moves the caret and nothing else. Recall resumes
 * the moment the buffer is empty again — or if the text is byte-identical to what
 * recall itself last wrote, which is what lets you keep walking after landing on
 * an entry.
 *
 * This rule has a consequence worth naming rather than discovering: a non-empty
 * buffer never navigates, so there is no buffer for a prefix filter to read.
 * zsh/fish-style prefix search is mutually exclusive with it by construction, and
 * is off the table until someone asks for `Ctrl+R`.
 */
export const TypedTextBlocksRecall: Story = {
  args: { history, initialText: "my own words" },
};

/**
 * A multi-line draft: ↑ moves the caret until it reaches the first line.
 *
 * The rule is zsh's `up-line-or-beginning-search` — does the text LEFT OF THE
 * CARET contain a newline — not "is the composer empty". Requiring an empty
 * composer made ↑ a dead key in any multi-line draft, which is where it is most
 * wanted.
 *
 * **The known limit, stated here rather than discovered by a user:** one long
 * line that WRAPS across three visual rows is ONE logical line, so ↑ from the
 * second visual row navigates instead of moving up a row. Doing better needs
 * pixel geometry from a live DOM. This is the live complaint against Claude Code
 * (anthropics/claude-code#63670), whose docs promise a visual-row rule its
 * shipped build does not implement. We promise the logical-line rule and
 * implement exactly that.
 *
 * Because the buffer is the user's, recall is refused here anyway — put the caret
 * on the first line and press ↑ to confirm the caret moves rather than the ladder.
 */
export const MultiLineDraft: Story = {
  args: {
    history,
    initialText: "first line\nsecond line\nthird line",
  },
};

/**
 * A queued prompt is a rung.
 *
 * Send once (the turn streams slowly), type a second prompt and send it too — it
 * joins the queue instead of vanishing. Now press ↑: the queued prompt is the
 * FIRST thing above your draft, because it was written but not answered and so is
 * nearer in time than anything already sent.
 *
 * Only the LAST queued prompt is a rung. Walking the whole queue would put
 * entries the user can already see, and remove, into a ladder they cannot see.
 */
export const QueuedPromptIsARung: Story = {
  args: {
    history,
    initialText: "check the server log",
    sendOnMount: true,
    script: tokenize("Reading the server log now, this will take a moment…"),
    delayMs: 320,
  },
};
