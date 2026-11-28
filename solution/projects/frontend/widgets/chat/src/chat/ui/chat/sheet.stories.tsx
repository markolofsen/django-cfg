import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";

import type { ChatMessage } from "../../core/conversation/parts";
import { mockAdapter } from "../../testing/mock-adapter";
import { Chat } from "./chat";

/**
 * The phone problem, reproducible without a phone.
 *
 * Storybook cannot raise a real on-screen keyboard, so the frame below does what the keyboard does to the page: it
 * shrinks the visible area (844 -> 480 px). Toggle it and the transcript must stay on the newest message; scroll up
 * first and it must NOT be yanked down. This exercises `Transcript`'s hold-bottom path (a resize of the scroller while
 * the content stays the same), which is the root cause of "the history jumps when the input gets focus". The sheet's
 * own `visualViewport` tracking needs a real device (see README, "What a real phone must confirm").
 */
const turn = (i: number): readonly ChatMessage[] => [
  {
    id: `u${i}`,
    role: "user",
    parts: [{ type: "text", id: `u${i}-t`, text: `Question ${i}: what changed in block ${i}?` }],
    status: { state: "complete" },
    createdAt: i * 10,
  },
  {
    id: `a${i}`,
    role: "assistant",
    parts: [{ type: "text", id: `a${i}-t`, text: `Answer ${i}: three things moved, the rest is unchanged. `.repeat(3) }],
    status: { state: "complete" },
    createdAt: i * 10 + 1,
  },
];
const history = Array.from({ length: 14 }, (_, i) => turn(i)).flat();

function PhoneFrame() {
  const [keyboard, setKeyboard] = useState(false);
  return (
    <div className="grid gap-3">
      <button className="w-fit rounded-md border px-3 py-1 text-sm" onClick={() => setKeyboard((k) => !k)}>
        {keyboard ? "Close keyboard (844px)" : "Open keyboard (480px)"}
      </button>
      <div
        className="chat-sheet-body overflow-hidden rounded-3xl border bg-background"
        style={{ width: 390, height: keyboard ? 480 : 844, transition: "height 250ms ease-out" }}
      >
        <Chat
          adapter={mockAdapter({ script: [], delayMs: 0 })}
          conversation={{ id: "phone", history }}
          body={{ kind: "packaged" }}
          className="flex min-h-0 flex-1 flex-col"
        />
      </div>
    </div>
  );
}

const meta = {
  title: "Widgets/Chat/Phone keyboard",
  component: PhoneFrame,
  parameters: { layout: "padded" },
} satisfies Meta<typeof PhoneFrame>;

export default meta;
type Story = StoryObj<typeof meta>;

export const KeyboardShrinksTheVisibleArea: Story = {};
