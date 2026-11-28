import type { Meta, StoryObj } from "@storybook/react-vite";

import type { ChatMessage } from "../../core/conversation/parts";
import { ChatMessageFrame, MessageProse } from "./message";

/**
 * The bubble decision, made visible.
 *
 * `ChatMessageFrame` and not `ChatMessageView`: the view resolves a message from
 * the store by id, which would need a provider and a seeded transcript to show
 * one visual state. The frame takes the message as a prop — the same split that
 * lets a subagent's nested thread reuse it — so each story below is a plain
 * value, and what is being judged is the frame and nothing else.
 *
 * These are organised by the decision each state can silently revert, not by
 * role. `message.bubble.test.ts` already ratchets those decisions in the
 * SOURCE; a ratchet can only prove a class name is present. Whether the result
 * is readable — that a reply is not framed against itself, that a pasted path
 * wraps instead of widening the transcript — is what needs an eye, and this is
 * where it gets one.
 */
const message = (over: Partial<ChatMessage> = {}): ChatMessage => ({
  id: "m1",
  role: "user",
  parts: [],
  status: { state: "complete" },
  createdAt: 0,
  ...over,
});

const meta = {
  title: "Widgets/Chat/Message",
  component: ChatMessageFrame,
  // Every story supplies its body through `render`, so the type would otherwise
  // demand a `children` arg none of them pass. Declaring it here once satisfies
  // the required prop and leaves each story to vary only the message.
  args: { message: message(), children: null },
  parameters: { a11y: { test: "error" } },
  decorators: [
    (Story) => (
      // A realistic column. The bubble is `w-fit`, so a full-bleed canvas would
      // hide the one thing worth checking: where the turn sits and how far it
      // is allowed to grow.
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-2 bg-background p-6">
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof ChatMessageFrame>;
export default meta;

// `typeof meta`, not `typeof ChatMessageFrame` — the two differ in what a story
// must repeat. Derived from meta, a story's `args` are checked against what meta
// ALREADY supplies, so it declares only what it varies; derived from the
// component, every story owes every required prop again. `satisfies` above is
// the other half: it checks the meta without widening it, which is what leaves
// the arg types for this line to read.
type Story = StoryObj<typeof meta>;

/** A user turn: bubbled, right-aligned, only as wide as its text. */
export const UserTurn: Story = {
  args: { message: message() },
  render: (args) => (
    <ChatMessageFrame {...args}>
      <MessageProse>Summarise the thread and show me the open questions.</MessageProse>
    </ChatMessageFrame>
  ),
};

/**
 * Only the user turn is bubbled.
 *
 * The reply gets the page: no background, no radius, full column, page text
 * colour. A frame around a long answer containing code and a plan competes with
 * the content it holds, which is why Vercel bubbles `is-user` only and why the
 * archive's two-bubble treatment was not taken.
 */
export const AssistantReplyIsNotBubbled: Story = {
  args: { message: message({ id: "m2", role: "assistant" }) },
  render: (args) => (
    <ChatMessageFrame {...args}>
      <MessageProse>
        The server is serving the current bundle. I stopped the process holding the
        previous embed in memory, rebuilt in the order that matters, and verified
        by hash rather than by the absence of a warning.
      </MessageProse>
    </ChatMessageFrame>
  ),
};

/** The pair, adjacent — the asymmetry only reads as deliberate in contrast. */
export const Exchange: Story = {
  args: { message: message() },
  render: () => (
    <>
      <ChatMessageFrame message={message()}>
        <MessageProse>Which file is the server actually running?</MessageProse>
      </ChatMessageFrame>
      <ChatMessageFrame message={message({ id: "m2", role: "assistant" })}>
        <MessageProse>
          `bin/app`, and it matches the current build. A stray binary keeps
          running from its unlinked inode, so the hash is the only answer that
          settles it.
        </MessageProse>
      </ChatMessageFrame>
    </>
  ),
};

/**
 * A pasted absolute path — one unbreakable token, and users paste them
 * constantly.
 *
 * Without `min-w-0` on the content column the token distends the flex child and
 * pushes the whole transcript sideways; without `break-words` it overflows the
 * bubble instead of wrapping inside it. Both are invisible until exactly this
 * input arrives, which is why it is a story and not a note.
 */
export const PastedPathMustNotWidenTheTranscript: Story = {
  args: { message: message() },
  render: (args) => (
    <ChatMessageFrame {...args}>
      <MessageProse>
        /Users/me/workspace/project/frontend/widgets/chat/src/ui/message/message.tsx
      </MessageProse>
    </ChatMessageFrame>
  ),
};

/**
 * The readable measure, and its limit.
 *
 * `MessageProse` caps prose near 72ch — but it is applied by the TEXT renderer,
 * never by the row. The un-wrapped block below is what a diff, a plan or a table
 * gets: the full column. Capping the row would have capped those too, and a
 * table truncated to prose width is unreadable in a way that looks deliberate.
 */
export const ProseIsCappedButWidgetsAreNot: Story = {
  args: { message: message({ id: "m2", role: "assistant" }) },
  render: (args) => (
    <ChatMessageFrame {...args}>
      <MessageProse>
        Long model prose stops at a readable line length, because a paragraph
        running the full width of a wide window forces the eye to hunt for the
        start of the next line — the cap is what keeps a long answer scannable
        rather than merely fitted to the container it happens to be in.
      </MessageProse>
      <div className="rounded border border-border bg-muted p-3 font-mono text-xs">
        This block registered its own part type, so it keeps the full column —
        the width a diff or a table needs.
      </div>
    </ChatMessageFrame>
  ),
};

/**
 * A failed turn must never read as something the agent said.
 *
 * The predecessor rendered failures as ordinary replies, which is worse than
 * silence: the reader attributes the text to the model. `interrupted` is
 * deliberately NOT given this treatment — it may still have been persisted and
 * reconciles on reconnect, so a verdict there would be a lie.
 */
export const FailedTurn: Story = {
  args: {
    message: message({
      id: "m2",
      role: "assistant",
      status: { state: "failed", message: "the server closed the stream" },
    }),
  },
  render: (args) => (
    <ChatMessageFrame {...args}>
      <MessageProse>The turn ended before the server finished it.</MessageProse>
    </ChatMessageFrame>
  ),
};
