import type { Meta, StoryObj } from "@storybook/react-vite";
import { Check, Copy, Pencil, RotateCcw } from "lucide-react";

import type { ChatMessage } from "../../core/conversation/parts";
import { ChatMessageFrame, MessageProse } from "./message";
import { MessageActions, type MessageAction } from "./actions";

/**
 * The action row, made visible in the states that can silently break.
 *
 * Two of them cannot be judged from source at all. Whether the transcript still
 * breathes correctly once every message carries a toolbar is only observable in
 * a column of several; whether the row is reachable without a pointer is only
 * observable by tabbing to it. Both are why this file exists beside the ratchet
 * test rather than instead of it.
 *
 * `actions` is a plain array in every story below — which is the point of the
 * seam. The host decides the inventory, so a story can express "one action" as
 * a value rather than by disabling two features.
 */
const message = (over: Partial<ChatMessage> = {}): ChatMessage => ({
  id: "m1",
  role: "assistant",
  parts: [],
  status: { state: "complete" },
  createdAt: 0,
  ...over,
});

const icon = "h-3.5 w-3.5";

const copy: MessageAction = {
  id: "copy",
  label: "Copy",
  icon: <Copy className={icon} aria-hidden />,
  onSelect: () => {},
};
const retry: MessageAction = {
  id: "retry",
  label: "Retry",
  icon: <RotateCcw className={icon} aria-hidden />,
  onSelect: () => {},
};
const edit: MessageAction = {
  id: "edit",
  label: "Edit",
  icon: <Pencil className={icon} aria-hidden />,
  onSelect: () => {},
};

const meta = {
  title: "Widgets/Chat/MessageActions",
  component: MessageActions,
  args: { message: message(), actions: [copy] },
  parameters: { a11y: { test: "error" } },
  decorators: [
    // `[&>*]:py-3` mirrors a host's own row padding, so the spacing the
    // frame's negative bottom margin is compensating is the real one.
    (Story) => (
      <div className="mx-auto flex w-full max-w-3xl flex-col bg-background p-6 [&>*]:py-3">
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof MessageActions>;
export default meta;

type Story = StoryObj<typeof meta>;

/**
 * The honest first cut: Copy, on the assistant turn.
 *
 * One control is not a failure — it is the row appearing at all, which is the
 * part that has to be right. Thumbs, share, sources and branching have no lane
 * in this product, and a row of controls that mostly cannot work is worse than
 * a smaller row that does.
 */
export const AssistantRow: Story = {
  args: { message: message(), actions: [copy] },
  render: (args) => (
    <ChatMessageFrame message={args.message} footer={<MessageActions {...args} />}>
      <MessageProse>
        `bin/app`, and it matches the current build. A stray binary keeps
        running from its unlinked inode, so the hash is the only answer that
        settles it.
      </MessageProse>
    </ChatMessageFrame>
  ),
};

/** On the user side the row sits under the bubble, right-aligned with it. */
export const UserRow: Story = {
  args: { message: message({ role: "user" }), actions: [copy, edit] },
  render: (args) => (
    <ChatMessageFrame message={args.message} footer={<MessageActions {...args} />}>
      <MessageProse>Which file is the server actually running?</MessageProse>
    </ChatMessageFrame>
  ),
};

/**
 * The state a second consumer starts in.
 *
 * A host with no retry lane passes one action and gets a correct row, not a
 * broken row with two dead controls. If this renders wrong, the seam is wrong.
 */
export const OneAction: Story = {
  args: { message: message(), actions: [copy] },
  render: (args) => (
    <ChatMessageFrame message={args.message} footer={<MessageActions {...args} />}>
      <MessageProse>A host that supplies exactly one action.</MessageProse>
    </ChatMessageFrame>
  ),
};

/** Every action a host can plausibly grow, to check the row at its widest. */
export const FullRow: Story = {
  args: { message: message(), actions: [copy, retry, edit] },
  render: (args) => (
    <ChatMessageFrame message={args.message} footer={<MessageActions {...args} />}>
      <MessageProse>Copy, retry and edit — the row at its widest.</MessageProse>
    </ChatMessageFrame>
  ),
};

/**
 * Hover one message in a column, and watch the others.
 *
 * The toolbar holds its place under every bubble at 10% and only brightens on
 * hover, so nothing moves; its height is given back by the frame's negative
 * bottom margin, which is why the rows sit as close as they would with no
 * actions at all. Tab through instead of hovering to check the other half: the
 * row must appear on focus, or these controls do not exist without a mouse.
 */
export const HoverDoesNotShiftTheTranscript: Story = {
  args: { message: message(), actions: [copy, retry] },
  render: () => (
    <>
      {["First reply in the column.", "Hover me.", "Third reply in the column."].map((text, i) => (
        <ChatMessageFrame
          key={text}
          message={message({ id: `m${i}` })}
          footer={<MessageActions message={message({ id: `m${i}` })} actions={[copy, retry]} />}
        >
          <MessageProse>{text}</MessageProse>
        </ChatMessageFrame>
      ))}
    </>
  ),
};

/** The confirmed state of Copy — the icon flips only after a real success. */
export const CopyConfirmed: Story = {
  args: {
    message: message(),
    actions: [
      {
        id: "copy",
        label: "Copied",
        icon: <Check className={`${icon} text-success`} aria-hidden />,
        onSelect: () => {},
      },
    ],
  },
  render: (args) => (
    <ChatMessageFrame message={args.message} footer={<MessageActions {...args} />}>
      <MessageProse>The check appears only when the write landed.</MessageProse>
    </ChatMessageFrame>
  ),
};
