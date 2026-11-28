import type { Meta, StoryObj } from "@storybook/react-vite";

import type { ChatMessage } from "../../core/conversation/parts";
import {
  CollapseTrigger,
  CollapsibleBody,
  useCollapse,
} from "./collapsible-body";
import { ChatMessageFrame, MessageProse } from "./message";

/**
 * A long turn bounded to a readable height.
 *
 * Three things here cannot be judged from source, which is why the stories
 * exist beside the policy test rather than instead of it: whether the cut lands
 * somewhere that reads as deliberate rather than as a rendering failure,
 * whether the control is findable in the toolbar without being loud, and
 * whether a short turn is left completely alone — the last being the one a
 * regression would make wrong everywhere at once.
 */
const message = (over: Partial<ChatMessage> = {}): ChatMessage => ({
  id: "m1",
  role: "assistant",
  parts: [],
  status: { state: "complete" },
  createdAt: 0,
  ...over,
});

const paragraph =
  "The server serves a committed bundle rather than your source, so a frontend change reaches the browser only after the bundle is synced and the process turns over. ";

/**
 * One row, assembled the way `ChatMessageView` assembles it: the row owns the
 * collapse, the body reads it, and the trigger sits in the toolbar.
 *
 * Stories build the row rather than the body alone precisely because the
 * control's PLACEMENT is the thing to look at — under the cut it overlapped the
 * clipped line, which is what moving it here fixed.
 */
function Row({
  times,
  streaming = false,
  collapsible = true,
  role = "assistant",
}: {
  readonly times: number;
  readonly streaming?: boolean;
  readonly collapsible?: boolean;
  readonly role?: ChatMessage["role"];
}) {
  const body = <MessageProse>{paragraph.repeat(times)}</MessageProse>;
  const collapse = useCollapse(streaming, times, collapsible);
  return (
    <ChatMessageFrame
      message={message({
        role,
        ...(streaming ? { status: { state: "streaming" } } : {}),
      })}
      footerEnd={<CollapseTrigger collapse={collapse} />}
    >
      <CollapsibleBody collapse={collapse}>{body}</CollapsibleBody>
    </ChatMessageFrame>
  );
}

const meta = {
  title: "Widgets/Chat/CollapsibleBody",
  component: CollapsibleBody,
  parameters: { layout: "padded" },
  decorators: [
    (Story) => (
      // `chat-surface` is required here, not decoration: the clamp is
      // `maxRows × --chat-text × --chat-leading`, and both tokens live on that
      // class. Without it the height budget falls back to defaults the real
      // transcript never uses, so the cut lands somewhere no reader will see.
      <div className="chat-surface mx-auto flex w-full max-w-3xl flex-col gap-2 bg-background p-6">
        <Story />
      </div>
    ),
  ],
} satisfies Meta<typeof CollapsibleBody>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * `collapse` and `children` are required on the component, so every story
 * declares them — each then overrides them in `render`, where the row is what
 * the story is actually about.
 */
const args = { collapse: undefined as never, children: null };

/** Short enough to fit: no clamp, and NO control in the toolbar. */
export const Short: Story = { args, render: () => <Row times={1} /> };

/** Past the budget: clipped, with the way in sitting in the toolbar. */
export const Long: Story = { args, render: () => <Row times={20} /> };

/**
 * Still arriving.
 *
 * Nothing folds and no control appears — the height belongs to the content
 * until the turn is finished.
 */
export const Streaming: Story = {
  args,
  render: () => <Row times={20} streaming />,
};

/**
 * The newest turn in the log.
 *
 * Never collapsed: there is nothing below it to scroll past, so the height it
 * would save buys the reader nothing, and folding the answer they are reading
 * right now is the opposite of the point.
 */
export const NewestTurn: Story = {
  args,
  render: () => <Row times={20} collapsible={false} />,
};

/**
 * The user's side, where the bubble has its own background.
 *
 * Worth its own story: the clamp lives inside the bubble's padding box, so a
 * cut that ignored it would run to the rounded edge.
 */
export const InUserBubble: Story = {
  args,
  render: () => <Row times={20} role="user" />,
};

/** Several rows together — the height actually saved is only visible in a column. */
export const InAColumn: Story = {
  args,
  render: () => (
    <div className="flex flex-col gap-6">
      {[20, 1, 14].map((times, index) => (
        <Row key={index} times={times} />
      ))}
      {/* The last row, left open, exactly as the transcript leaves it. */}
      <Row times={20} collapsible={false} />
    </div>
  ),
};
