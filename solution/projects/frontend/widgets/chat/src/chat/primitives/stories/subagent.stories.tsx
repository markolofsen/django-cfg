import type { Meta, StoryObj } from "@storybook/react-vite";

import type { ChatMessage } from "../../core/conversation/parts";
import { Harness } from "./harness";

/**
 * The subagent thread, in its own file.
 *
 * Separate from `transcript.stories.tsx` because it is seeded from HISTORY
 * rather than scripted from chunks: `ToolPart.messages` has no frame in the
 * wire vocabulary, so these two story sets reach the transcript by different
 * doors and only share the workbench.
 */

const meta = {
  title: "Widgets/Chat/Subagent",
  component: Harness,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof Harness>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * The subagent's own conversation.
 *
 * Real `ChatMessage` values, and they never enter the store: they live on
 * `ToolPart.messages`, which is why `MessageContent` exists beside `Message`
 * (`primitives/parts/message.tsx`) — `useMessage(id)` would find nothing for any of
 * these ids. The nested `grep` call is deliberate: it is a tool part rendered
 * by the SAME `ToolPart` renderer as the outer one, through the inherited
 * registry, and it is what fails visibly if inheritance ever regresses.
 */
const subagentTurn: readonly ChatMessage[] = [
  {
    id: "s-user",
    role: "user",
    parts: [{ type: "text", id: "s-user-t", text: "Find every TODO under core/server." }],
    status: { state: "complete" },
    createdAt: 0,
  },
  {
    id: "s-tool",
    role: "assistant",
    parts: [
      {
        type: "tool",
        id: "s-grep",
        toolName: "grep",
        toolState: {
          state: "output-available",
          input: { pattern: "TODO", path: "core/server" },
          output: "core/server/http/ask.go:212\ncore/server/storage/db.go:88",
        },
      },
    ],
    status: { state: "complete" },
    createdAt: 1,
  },
  {
    id: "s-answer",
    role: "assistant",
    parts: [{ type: "text", id: "s-answer-t", text: "Two TODOs, both in core/server." }],
    status: { state: "complete" },
    createdAt: 2,
  },
];

export const Subagent: Story = {
  args: {
    script: [],
    history: [
      {
        id: "u1",
        role: "user",
        parts: [{ type: "text", id: "u1-t", text: "Audit core/server for leftovers." }],
        status: { state: "complete" },
        createdAt: 10,
      },
      {
        id: "a1",
        role: "assistant",
        parts: [
          {
            type: "tool",
            id: "task-1",
            toolName: "Task",
            toolState: {
              state: "output-available",
              input: { prompt: "Find every TODO under core/server." },
              output: "2 findings",
            },
            messages: subagentTurn,
          },
          { type: "text", id: "a1-t", text: "The subagent found two TODOs; both are in the parser." },
        ],
        status: { state: "complete" },
        createdAt: 11,
      },
    ],
  },
};
