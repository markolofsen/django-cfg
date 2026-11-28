import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, userEvent, within } from "storybook/test";

import { mockVoice, tokenize } from "../../testing";
import { ComposerHarness } from "./harness";

/**
 * The composer, in the states that only exist mid-input.
 *
 * These cover what an assertion cannot: whether the pieces FIT, assembled the
 * way a host must assemble them. Building this workbench surfaced a real gap —
 * `ComposerInput` owned Enter outright and exposed no seam, so a menu could not
 * claim the key it needs. That is now the `onKeyDown`/`defaultPrevented`
 * protocol both references use.
 *
 * `@`-mentions live on their own page (`composer-mentions.stories.tsx`): they are
 * one subject with one fixture, and they moved out when this file crossed its
 * 300-line budget.
 */
const meta = {
  title: "Widgets/Chat/Composer",
  component: ComposerHarness,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof ComposerHarness>;

export default meta;
type Story = StoryObj<typeof meta>;

const reply = "Checked the server log: three warnings, one closed stream.";

// A counter, not `Math.random()`: story fixtures must be deterministic, and a
// random id would make two runs of the same story differ in the DOM.

/** Empty and idle. Send is disabled — there is nothing to send. */
export const Empty: Story = {
  args: {},
};

/** Text in the field: Send becomes available. */
export const Ready: Story = {
  args: { initialText: "Summarise the thread" },
};

/**
 * The textarea grows with its content and then scrolls.
 *
 * Autosize is a `useLayoutEffect` for a reason worth seeing: measured in an
 * ordinary effect, every keystroke paints one frame at the old height. The cap
 * is `maxRows`, after which the box scrolls instead of pushing the transcript
 * off screen.
 */
export const GrowsWithContent: Story = {
  args: {
    initialText: [
      "Walk me through what happens on `make ship`:",
      "",
      "1. sync the embed",
      "2. build in the order that matters",
      "3. restart so the running process serves the new bundle",
      "4. verify by hash, never by the absence of a warning",
    ].join("\n"),
  },
};

/**
 * Mid-turn: Send has become Stop.
 *
 * One button, two jobs — `ComposerSend` reads `isStreaming` and swaps both the
 * action and its accessible name. A second, separately-rendered stop button is
 * how a UI ends up with a disabled Send beside an active Stop and no way to
 * tell which one the Enter key means.
 *
 * `sendOnMount` plus a slow script is what parks the story mid-turn. Both are
 * needed: without the send nothing streams, and this workbench stays silent by
 * default so the other stories keep their draft. Before the send existed this
 * story rendered an idle Send while its own title said Stop — a doc comment is
 * not a gate, and only the browser disagreed with it.
 */
export const Streaming: Story = {
  args: {
    initialText: "Check the server log",
    sendOnMount: true,
    delayMs: 400,
    script: [
      { type: "message-start", messageId: "a1", createdAt: 0 },
      ...tokenize(reply),
      { type: "finish" },
    ],
  },
};

/**
 * A prompt written while the agent is still working.
 *
 * Press Send once (the turn starts and streams slowly), then type again and
 * press Send: the second prompt joins a queue instead of vanishing. It drains
 * ITSELF when the turn ends — there is no "go" button, because a queue that
 * needed one would be a to-do list.
 *
 * What this replaces was one line in the store — `if (state.inFlight !== null)
 * return;` — which discarded the second turn in silence: no error, no toast, the
 * text simply gone from the field. Our agents run for minutes, so that was
 * precisely the moment a user was most likely to have something to add.
 *
 * Collapsed by default. The summary answers the only question the user actually
 * has ("did it take my message?"); the list is for the rarer moment they want to
 * drop one. Press Stop and the queue SURVIVES — Stop must not start something.
 */
export const QueuedPrompts: Story = {
  args: {
    initialText: "Check the server log",
    sendOnMount: true,
    // Slow enough to type a second prompt while the first is still streaming.
    script: tokenize("Reading the server log now, this will take a moment…"),
    delayMs: 320,
  },
};

/**
 * A queued prompt stays RELEASABLE after Stop.
 *
 * Stop refuses to drain the queue — deliberately, so Stop cannot start
 * something. But the release control used to require a running turn, so the
 * moment Stop ended it the button vanished and the prompt sat with only "edit"
 * and "remove". It read as the message having been swallowed by the interrupt,
 * which is the exact report this fixes.
 *
 * This harness passes no `confirmSendNow`, which is a REAL configuration and
 * what makes the story precise: with no host dialog the interrupting control is
 * correctly withheld while the turn streams (an unconfirmed interrupt is the one
 * shape that must never ship), so the button below can only be the idle one.
 * Measured — while streaming the row renders exactly `edit` and `remove`.
 *
 * MUTANT: gate the control on `isStreaming` again → nothing appears after Stop
 * and the final assertion fails, while every other queue story stays green.
 */
export const AQueuedPromptSurvivesStop: Story = {
  args: {
    initialText: "Check the server log",
    sendOnMount: true,
    script: tokenize("Reading the server log now, this will take a moment…"),
    delayMs: 320,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Queue a second prompt behind the streaming first one. The row appears,
    // carrying no release control yet — see the note above.
    const field = canvas.getByRole("textbox");
    await userEvent.type(field, "And check the disk too{Enter}");
    await expect(await canvas.findByRole("button", { name: "Remove from queue" })).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Send now" })).toBeNull();

    // Stop ends the turn. The queue survives, and now so does a way to release
    // it — named as a plain send, because there is no longer a reply to stop.
    await userEvent.click(canvas.getByRole("button", { name: "Stop" }));
    await expect(await canvas.findByRole("button", { name: "Send now" })).toBeVisible();
  },
};

/**
 * Dictation, offered.
 *
 * The mic exists because the story passes a `voice` capability — and ONLY then.
 * Compare with every other story on this page: none of them render a
 * microphone, which is the contract working, not a missing button.
 *
 * That absence is the whole reason these three stories exist. `core/voice`
 * can hold a full state machine and green tests while NO component mounts it
 * and no story renders it: every other rung agrees the feature is fine and
 * none can see that it reached no screen. A story is the only rung that fails
 * on that.
 *
 * Press it to dictate — the transcript is scripted, so no microphone and no
 * permission prompt are involved.
 */
export const VoiceIdle: Story = {
  args: {
    capabilities: { voice: mockVoice() },
  },
};

/**
 * Mid-sentence: an interim result REPLACES its predecessor.
 *
 * The engine re-sends its whole current guess — "summarise the", "summarise the last" —
 * so appending would duplicate the sentence in front of the user. `VoiceSession`
 * absorbs that, and this story is where you can watch it not happen.
 *
 * The draft is seeded, so it also shows the ANCHOR: dictation appends to text
 * the user already typed rather than replacing it. That rule lives in
 * `ComposerVoice`, not in the session — what was typed before is composer state.
 */
export const VoiceRecording: Story = {
  args: {
    capabilities: { voice: mockVoice({ delayMs: 700 }) },
    initialText: "Note:",
  },
};

/**
 * A denied microphone.
 *
 * The realistic failure — the user presses the mic and clicks "Block". It
 * settles on the snapshot as an error and the button returns to idle; nothing
 * throws, because an unhandled rejection while someone is mid-sentence is how a
 * composer loses a draft.
 */
export const VoiceDenied: Story = {
  args: {
    capabilities: { voice: mockVoice({ failWith: "Microphone permission denied" }) },
  },
};
