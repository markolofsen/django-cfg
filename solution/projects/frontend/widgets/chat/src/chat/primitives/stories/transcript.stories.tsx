import type { Meta, StoryObj } from "@storybook/react-vite";

import { tokenize } from "../../testing/mock-adapter";
import { Harness } from "./harness";

/**
 * Stories on the PRIMITIVES, not on `<Chat>`.
 *
 * A story of the packaged component can only vary its seven props; these vary
 * the states that actually break — a tool call mid-stream, a failed turn, a
 * retry. That is what `@rules/architecture.md` means by "Storybook on
 * primitives": the workbench has to reach the states, not the wrapper.
 *
 * Every story here is SCRIPTED from chunks, so each one also exercises the
 * adapter contract. The history-seeded case lives in `subagent.stories.tsx`.
 *
 * Tool calls have their own file (`tool-call.stories.tsx`) — one subject, one
 * owner. What belongs HERE is the turn's own lifecycle: streaming, empty,
 * reasoning, failed, interrupted, reset.
 */

const meta = {
  title: "Widgets/Chat/Transcript",
  component: Harness,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof Harness>;

export default meta;
type Story = StoryObj<typeof meta>;

const reply = "Here is what I found in the log — three warnings and one error.";

export const Streaming: Story = {
  args: {
    script: [
      { type: "message-start", messageId: "a1", createdAt: 0 },
      ...tokenize(reply),
      { type: "finish" },
    ],
  },
};

export const Empty: Story = {
  args: { script: [], prompt: "" },
};

export const WithReasoning: Story = {
  args: {
    script: [
      { type: "message-start", messageId: "a1", createdAt: 0 },
      { type: "reasoning-start", partId: "r1" },
      { type: "reasoning-delta", partId: "r1", delta: "The log has 4 lines worth reading." },
      ...tokenize(reply),
      { type: "finish" },
    ],
  },
};

/** A failed turn must not read as an ordinary reply — that is the whole point. */
export const Failed: Story = {
  args: {
    script: [
      { type: "message-start", messageId: "a1", createdAt: 0 },
      { type: "text-start", partId: "t1" },
      { type: "text-delta", partId: "t1", delta: "Let me check tha" },
      { type: "error", message: "upstream 502" },
    ],
  },
};

export const Interrupted: Story = {
  args: {
    script: [
      { type: "message-start", messageId: "a1", createdAt: 0 },
      { type: "text-start", partId: "t1" },
      { type: "text-delta", partId: "t1", delta: "Connection dropped mid-" },
      { type: "interrupted" },
    ],
  },
};

/**
 * Sent, and nothing back yet — the gap an agent spends reading files or
 * starting a subagent, which here is the common case rather than an edge one.
 *
 * A long delay before the first chunk is what holds the state open. Without an
 * indicator this frame shows the user's bubble and then silence, and the only
 * evidence the turn is alive sits on the Stop button in the far corner.
 */
export const Pending: Story = {
  args: {
    delayMs: 60_000,
    script: [
      { type: "message-start", messageId: "a1", createdAt: 0 },
      ...tokenize(reply),
      { type: "finish" },
    ],
  },
};

/**
 * The indicator gives way to the reply itself, on the FIRST part rather than at
 * turn-end — otherwise a streaming answer renders under a "waiting" label.
 */
export const PendingThenStreams: Story = {
  args: {
    delayMs: 700,
    script: [
      { type: "message-start", messageId: "a1", createdAt: 0 },
      ...tokenize(reply),
      { type: "finish" },
    ],
  },
};

/** The retry instruction: the abandoned fragment must NOT survive. */
export const StreamReset: Story = {
  args: {
    delayMs: 90,
    script: [
      { type: "message-start", messageId: "a1", createdAt: 0 },
      { type: "text-start", partId: "t1" },
      { type: "text-delta", partId: "t1", delta: "abandoned half-sentence that" },
      { type: "reset" },
      ...tokenize(reply, "t2"),
      { type: "finish" },
    ],
  },
};
