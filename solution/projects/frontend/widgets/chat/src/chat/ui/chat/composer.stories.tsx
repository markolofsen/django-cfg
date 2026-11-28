import type { Meta, StoryObj } from "@storybook/react-vite";
import { useCallback, useState } from "react";
import { useDialog } from "@djangocfg/ui-core/lib/dialog-service";

import type { AttachmentsCapability } from "../../core/compose/attachments";
import { emptyDraft } from "../../core/compose/outbound";
import { ChatProvider, createChatStore } from "../../store";
import { mockAdapter, tokenize } from "../../testing";
import { ChatComposer, type ChatComposerProps } from "./composer";

/**
 * The SHIPPED composer, not the workbench.
 *
 * `composer.stories.tsx` renders the harness, which styles its own rows — so
 * every visual decision in `chat-composer.tsx` (row geometry, hit boxes, where
 * the queue controls sit) was unseen. The queue shipped with its label rendered
 * as text and took the whole row from the prompt before anyone looked.
 */
const meta = {
  title: "Widgets/Chat/Composer view",
  component: ChatComposer,
  parameters: { layout: "padded", a11y: { test: "error" } },
} satisfies Meta<typeof ChatComposer>;

export default meta;
type Story = StoryObj<typeof meta>;

let seq = 0;
const nextId = () => `id_${++seq}`;

/**
 * A store parked mid-turn with prompts already queued.
 *
 * Seeded through `send` rather than by typing: the queue only fills while a
 * turn runs, and driving that from a story means racing a token stream. The
 * first send starts the turn, the rest queue behind it — which is the real
 * mechanism, not a fixture standing in for it.
 */
function parked(prompts: readonly string[]) {
  const store = createChatStore({
    adapter: mockAdapter({
      // Long enough that the turn is still running while the story is read.
      script: tokenize("Reading the server log now, this will take a moment…"),
      delayMs: 4000,
    }),
    makeId: nextId,
    now: () => 0,
  });
  for (const text of prompts) void store.send({ ...emptyDraft, text });
  return store;
}

const confirm = () => Promise.resolve(true);

/**
 * One prompt queued while the agent works.
 *
 * Both controls are icon-only. Their labels are full sentences in every locale
 * ("Отправить сейчас, прервав текущий ответ"), which is right for an accessible
 * name and wrong for a row — rendered as text it left the prompt itself squeezed
 * into the corner. Hover either button to read the label as a tooltip.
 */
export const QueuedPrompt: Story = {
  args: { confirmSendQueuedNow: confirm },
  render: (args) => (
    <ChatProvider adapter={mockAdapter({ script: [] })} store={parked(["Check the server log", "and then restart the agent"])}>
      <ChatComposer {...args} />
    </ChatProvider>
  ),
};

/**
 * A multi-line prompt.
 *
 * The row caps at `max-h-20` and scrolls rather than truncating — a queued
 * prompt is a message the user has not seen sent, so hiding part of it is the
 * failure the strip exists to prevent. The controls stay on the FIRST line
 * (`self-start`) rather than centring against a paragraph.
 */
export const LongQueuedPrompt: Story = {
  args: { confirmSendQueuedNow: confirm },
  render: (args) => (
    <ChatProvider
      adapter={mockAdapter({ script: [] })}
      store={parked([
        "Check the server log",
        "then walk the last hour of it, group the errors by host, and tell me which of them started after the deploy rather than before it",
      ])}
    >
      <ChatComposer {...args} />
    </ChatProvider>
  ),
};

/**
 * Past the inline limit, only the TAIL folds away.
 *
 * The composer sits at the bottom of the transcript, so an unbounded list grows
 * upward into it — but hiding every row replaces the queue with a bare count,
 * and the rows the user can see are what the strip is for. Three stay; the rest
 * become one line. Click it to expand.
 *
 * FIVE prompts for four visible rows: `parked` sends them all, so the first is
 * the running turn and never reaches the queue.
 */
export const CollapsedQueue: Story = {
  args: { confirmSendQueuedNow: confirm },
  render: (args) => (
    <ChatProvider
      adapter={mockAdapter({ script: [] })}
      store={parked(["first", "second", "third", "fourth", "fifth"])}
    >
      <ChatComposer {...args} />
    </ChatProvider>
  ),
};

/**
 * No confirmation available ⇒ no interrupt control at all.
 *
 * Only the remove button remains. An unconfirmed interrupt destroys a running
 * turn on one click, which is the one shape this must never ship, so the
 * control is absent rather than present-and-unguarded.
 */
export const NoInterruptWithoutConfirmation: Story = {
  args: {},
  render: (args) => (
    <ChatProvider
      adapter={mockAdapter({ script: [] })}
      store={parked(["Check the server log", "and then restart the agent"])}
    >
      <ChatComposer {...args} />
    </ChatProvider>
  ),
};

/**
 * Taking a queued prompt back when the field already holds something.
 *
 * TYPE INTO THE FIELD FIRST, then click a queued row. With the field empty
 * nothing is at risk and the write must not ask — that is `needsChoice`, and it
 * is why this story cannot seed the draft for you.
 *
 * Answering NO leaves both sides untouched: the caller holds the prompt in the
 * queue until the answer arrives, so declining is not a way to lose it.
 *
 * The dialog is ui-core's `confirm`, the SAME one the app wires — a story that
 * rolled its own would demonstrate a surface the product does not ship. Its
 * provider is mounted once by the global harness, so this only consumes it.
 */
function ReplaceDemo(args: Partial<ChatComposerProps>) {
  const { confirm } = useDialog();
  const askReplaceDraft = useCallback(
    () =>
      confirm({
        title: "Replace what you have typed?",
        message: "Your draft will be replaced by this queued prompt.",
        variant: "destructive",
      }),
    [confirm],
  );
  return (
    <ChatProvider
      adapter={mockAdapter({ script: [] })}
      store={parked(["Check the server log", "and then restart the agent"])}
    >
      <ChatComposer {...args} askReplaceDraft={askReplaceDraft} />
    </ChatProvider>
  );
}

export const ReplaceOrKeepDraft: Story = {
  args: {},
  render: (args) => <ReplaceDemo {...args} />,
};

/** A host `upload` that reports progress over ~1.2 s and refuses a file named `fail*`. */
const fakeUpload: AttachmentsCapability["upload"] = async (file, { signal, onProgress }) => {
  for (let step = 1; step <= 6; step += 1) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    if (signal.aborted) throw new DOMException("aborted", "AbortError");
    onProgress(step / 6);
  }
  if (file.name.startsWith("fail")) throw new Error("The server refused this file");
  return { url: URL.createObjectURL(file) };
};

/**
 * Attachments: the paperclip, drag-and-drop onto the box and paste of an image.
 *
 * Defaults except for a 2 MB limit and two files, so a refusal is easy to see:
 * add a video (kind not enabled), a file over 2 MB, a third file, or a file
 * named `fail.txt` (the host's upload rejecting).
 */
export const Attachments: Story = {
  render: (args) => (
    <ChatProvider
      adapter={mockAdapter({ script: [] })}
      capabilities={{ attachments: { upload: fakeUpload, maxFileSize: 2 * 1024 * 1024, maxFiles: 2 } }}
    >
      <ChatComposer {...args} />
    </ChatProvider>
  ),
};

function ModelsDemo(args: Partial<ChatComposerProps>) {
  const [value, setValue] = useState("auto");
  return (
    <ChatProvider
      adapter={mockAdapter({ script: [] })}
      capabilities={{
        models: {
          value,
          onChange: setValue,
          options: [
            { id: "auto", label: "Auto", hint: "Picks the model for the question" },
            { id: "fast", label: "Fast", hint: "Quick answers" },
            { id: "smart", label: "Smart", hint: "Slower, for hard questions" },
          ],
        },
      }}
    >
      <ChatComposer {...args} />
    </ChatProvider>
  );
}

/** The model switch: a chip in the control row that opens a radio menu; the id rides on the request. */
export const Models: Story = { render: (args) => <ModelsDemo {...args} /> };
