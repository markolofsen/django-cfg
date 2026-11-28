import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";

import { ActionCard, type ActionCardProps } from "./actions/card";
import type { Proposal, ProposedAction } from "./actions/proposal";

/**
 * The proposal card: the surface of the confirmation gate.
 *
 * Every story renders the card against a real form, because what the card
 * claims it will do and what the page then does are the same assertion. The
 * gate itself (`useProposals`) is not wired here — a story that could write to
 * the page would be a story that runs an unapproved action.
 */

const CLICK: ProposedAction = { kind: "click", ref: "@e1" };
const FILL: ProposedAction = { kind: "fill", ref: "@e2", value: "ada@example.com" };

function pending(id: string, action: ProposedAction, label: string): Proposal {
  return { id, action, label, state: { status: "pending" } };
}

/**
 * The host page the agent is looking at, drawn beside the card.
 *
 * Hovering an element here reports its ref back, so the link runs BOTH ways:
 * the card names an element, and an element names the card that targets it.
 * One direction alone leaves the user hovering the page and seeing nothing.
 */
function Page({
  highlighted,
  onHover,
}: {
  highlighted: string | null;
  onHover: (ref: string | null) => void;
}) {
  const ring = (ref: string) =>
    highlighted === ref ? "outline outline-2 outline-primary outline-offset-2" : "";
  const hover = (ref: string) => ({
    onMouseEnter: () => onHover(ref),
    onMouseLeave: () => onHover(null),
  });
  return (
    <div className="flex w-64 flex-col gap-3 rounded-[var(--radius)] border border-border p-4">
      <label className="flex flex-col gap-1 text-xs text-muted-foreground">
        Email
        <input
          className={`h-8 rounded-[var(--radius-sm)] border border-input px-2 text-sm ${ring("@e2")}`}
          defaultValue=""
          readOnly
          {...hover("@e2")}
        />
      </label>
      <button
        className={`h-8 rounded-[var(--radius)] bg-primary text-sm text-primary-foreground ${ring("@e1")}`}
        type="button"
        {...hover("@e1")}
      >
        Save
      </button>
    </div>
  );
}

/**
 * Card and page side by side, with the card's preview driving the highlight.
 *
 * Takes the card's own props rather than just the proposal, so `args` is what
 * the story actually renders — the typing pair only checks args that reach the
 * component.
 */
function Stage({ proposal, onPreview }: ActionCardProps) {
  const [highlighted, setHighlighted] = useState<string | null>(null);
  return (
    <div className="flex items-start gap-6">
      <div className="w-72">
        <ActionCard
          proposal={proposal}
          onApprove={() => {}}
          onReject={() => {}}
          onPreview={(ref) => {
            setHighlighted(ref);
            onPreview?.(ref);
          }}
        />
      </div>
      <Page highlighted={highlighted} onHover={setHighlighted} />
    </div>
  );
}

const meta = {
  title: "Widgets/Chat/PageCopilot",
  component: ActionCard,
  tags: ["autodocs"],
  parameters: {
    docs: {
      description: {
        component:
          "A proposed page action, awaiting yes or no. Nothing reaches the page until the user answers.",
      },
    },
  },
} satisfies Meta<typeof ActionCard>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Hovering the card highlights the element it names. This is the whole point of
 * the ref: the user sees WHICH button before agreeing to press it.
 */
export const Highlight: Story = {
  args: {
    proposal: pending("s1", CLICK, "the Save button"),
    onApprove: () => {},
    onReject: () => {},
  },
  render: (args) => <Stage {...args} />,
};

/** A proposed click, unanswered — the ordinary case. */
export const ProposeClick: Story = {
  args: {
    proposal: pending("s2", CLICK, "the Save button"),
    onApprove: () => {},
    onReject: () => {},
  },
  render: (args) => <Stage {...args} />,
};

/**
 * A fill shows the text it will type. The value is part of what is being
 * approved, so it is on the card rather than behind a disclosure.
 */
export const ProposeFill: Story = {
  args: {
    proposal: pending("s3", FILL, "the email field"),
    onApprove: () => {},
    onReject: () => {},
  },
  render: (args) => <Stage {...args} />,
};

/** Approved and done. The card stays as the record of what the user answered. */
export const Approved: Story = {
  args: {
    proposal: {
      ...pending("s4", CLICK, "the Save button"),
      state: { status: "settled", outcome: "approved" },
    },
    onApprove: () => {},
    onReject: () => {},
  },
  render: (args) => <Stage {...args} />,
};

/** Declined. A refusal is an answer — the agent is told, and does not re-propose. */
export const Rejected: Story = {
  args: {
    proposal: {
      ...pending("s5", CLICK, "the Save button"),
      state: { status: "settled", outcome: "rejected" },
    },
    onApprove: () => {},
    onReject: () => {},
  },
  render: (args) => <Stage {...args} />,
};

/**
 * The page moved between proposing and answering. The ref is re-resolved at
 * approval time, so a vanished target is reported rather than acted on by
 * position — a positional selector names a slot, and the next element would
 * have matched it.
 */
export const StaleRef: Story = {
  args: {
    proposal: {
      ...pending("s6", CLICK, "the Save button"),
      state: { status: "settled", outcome: "stale" },
    },
    onApprove: () => {},
    onReject: () => {},
  },
  render: (args) => <Stage {...args} />,
};
