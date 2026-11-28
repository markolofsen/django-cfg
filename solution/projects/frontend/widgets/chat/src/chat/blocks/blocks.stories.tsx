import type { Meta, StoryObj } from "@storybook/react-vite";

import { ApprovalBlock, AskBlock, ChangesBlock } from "./index";

/**
 * The interactive blocks an answer can carry, drawn straight from their payloads (the chat wires the same components to its store through `BlockRenderer`, with `kind` ask / approval / changes).
 * Each is shown open and settled: a settled block is what a reloaded transcript draws.
 */
const noop = () => undefined;

const meta = {
  title: "Widgets/Chat/Blocks",
  component: AskBlock,
  // Every story draws its own block through `render`; these only satisfy the component's required props.
  args: { data: { options: [], other: true }, onAnswer: noop },
  parameters: { layout: "padded" },
  decorators: [(Story) => <div className="mx-auto max-w-md"><Story /></div>],
} satisfies Meta<typeof AskBlock>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Question: Story = {
  render: () => (
    <AskBlock
      data={{ question: "Which Tenerife contact should I keep?", options: [{ label: "Katerina Gordeeva", description: "Added 2 March" }, { label: "Helen" }, { label: "Nika" }], other: "Someone else…" }}
      onAnswer={noop}
    />
  ),
};

export const QuestionSettled: Story = {
  render: () => <AskBlock data={{ question: "Apply to every contact?", options: [{ label: "Yes" }, { label: "No" }], other: false }} onAnswer={noop} settled />,
};

export const FreeAnswer: Story = {
  render: () => <AskBlock data={{ question: "What should the database be called?", options: [], other: true }} onAnswer={noop} />,
};

export const Approval: Story = {
  render: () => (
    <ApprovalBlock
      data={{ summary: "Store export dates as timestamps", changes: [{ path: "export.created_at", from: "text", to: "timestamp" }, { path: "export.updated_at", from: "text", to: "timestamp" }] }}
      onDecide={noop}
    />
  ),
};

export const Changes: Story = {
  render: () => (
    <ChangesBlock
      data={{ title: "Merged the contacts and updated the review list", undoable: true, items: ["Katerina Gordeeva", "Helen", "Ваня Тюменев", "Nika", "Alan Tenerifebook", "Yauhenu Tenerifebook"].map((label) => ({ label })) }}
      onUndo={noop}
    />
  ),
};
