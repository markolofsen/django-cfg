import type { Meta, StoryObj } from "@storybook/nextjs-vite";
import { useMemo, useState } from "react";

import { Chat, DataRenderer } from "@djangocfg/widget-chat";
import type { PartRenderProps, StreamChunk } from "@djangocfg/widget-chat";
import { Response } from "@djangocfg/widget-chat/content";
import { PageSnapshotProvider, usePageSnapshot } from "@djangocfg/widget-chat/page-snapshot";
import {
  createActionRenderer,
  usePageCopilot,
  useProposals,
  type PageAwareAdapter,
  type PageTurn,
} from "@djangocfg/widget-chat/copilot";

/**
 * The whole feature, wired: a chat that sees the page and proposes actions on it.
 *
 * Three seams, none of which touch `widget-chat`:
 *
 *  - `usePageCopilot` wraps the host's adapter, so the page rides every turn.
 *  - `useProposals` is the gate: nothing reaches the page until Approve.
 *  - `createActionRenderer` draws `ui-action` blocks as cards, delegating every
 *    other data kind back to the chat's own renderer.
 *
 * The adapter is a local fake — it reads the snapshot it was handed and
 * proposes against real refs from THIS page. No backend, but the refs are not
 * invented: they come from the capture.
 */

/**
 * Every `@eN` in a captured tree, in DOM order.
 *
 * Walks the tree rather than reading a ref list off the payload, because that
 * is what the model does: refs exist for it only where they appear in the CST
 * it was shown.
 */
function collectRefs(node: unknown, out: string[] = []): string[] {
  if (typeof node !== "object" || node === null) return out;
  const record = node as { ref?: unknown; children?: unknown };
  if (typeof record.ref === "string") out.push(record.ref);
  if (Array.isArray(record.children)) {
    for (const child of record.children) collectRefs(child, out);
  }
  return out;
}

/** The first node of a given role in the capture, with its ref and its name. */
function findRef(turn: PageTurn, role: string): { ref: string; name: string } | null {
  if (turn.page?.kind !== "snapshot") return null;
  const found: { ref: string; name: string }[] = [];
  const walk = (node: unknown): void => {
    if (typeof node !== "object" || node === null) return;
    const record = node as {
      ref?: unknown;
      role?: unknown;
      name?: unknown;
      children?: unknown;
    };
    if (typeof record.ref === "string" && record.role === role) {
      found.push({
        ref: record.ref,
        name: typeof record.name === "string" && record.name ? record.name : role,
      });
    }
    if (Array.isArray(record.children)) record.children.forEach(walk);
  };
  walk(turn.page.payload.snapshot);
  return found[0] ?? null;
}

/** A scripted agent: answers in text, then proposes one action per request. */
function useFakeAdapter(): PageAwareAdapter {
  return useMemo((): PageAwareAdapter => {
    let turnCount = 0;
    return {
      async sendMessage(request, turn) {
        turnCount += 1;
        const id = `m${turnCount}`;
        // The refs the agent may cite come from the capture it was given —
        // read out of the TREE, which is what a real model reads. Nothing here
        // guesses: no snapshot means no proposal.
        const refs = turn.page?.kind === "snapshot" ? collectRefs(turn.page.payload.snapshot) : [];
        const text = request.text;
        const wantsFill = /fill|email|заполн/i.test(text);

        const chunks: StreamChunk[] = [
          { type: "message-start", messageId: id, createdAt: Date.now() },
          { type: "text-start", partId: `${id}t` },
          {
            type: "text-delta",
            partId: `${id}t`,
            delta: refs.length
              ? `I can see ${refs.length} elements on this page. Here is what I propose:`
              : "I cannot see the page yet — turn on the page link first.",
          },
        ];

        // Cite a ref that is actually IN the capture. A demo that hardcoded
        // `@e1` would keep working when the resolution broke, which is the one
        // thing a live wiring exists to catch.
        const target = wantsFill ? findRef(turn, "textbox") : findRef(turn, "button");

        if (target) {
          chunks.push({
            type: "data",
            part: {
              id: `${id}a`,
              type: "data",
              kind: "ui-action",
              data: wantsFill
                ? {
                    id: `${id}-fill`,
                    label: target.name,
                    action: { kind: "fill", ref: target.ref, value: "ada@example.com" },
                  }
                : {
                    id: `${id}-click`,
                    label: target.name,
                    action: { kind: "click", ref: target.ref },
                  },
            },
          });
        }

        chunks.push({ type: "finish" });

        return new ReadableStream<StreamChunk>({
          start(controller) {
            for (const chunk of chunks) controller.enqueue(chunk);
            controller.close();
          },
        });
      },
    };
  }, []);
}

/**
 * A loaded, empty room — one stable identity for the life of the module.
 *
 * The store compares this to decide "the conversation changed", so a fresh
 * object each render reads as a new room and reseeds the transcript.
 */
const EMPTY_ROOM = { history: [] as const };

/** The page the agent looks at — a real form, captured by the snapshot engine. */
function DemoForm() {
  const [email, setEmail] = useState("");
  const [saved, setSaved] = useState<string | null>(null);
  return (
    <form
      className="flex w-72 flex-col gap-3 rounded-[var(--radius)] border border-border p-4"
      onSubmit={(event) => event.preventDefault()}
    >
      <h3 className="text-sm font-semibold">Profile</h3>
      <label className="flex flex-col gap-1 text-xs text-muted-foreground">
        Email
        <input
          className="h-8 rounded-[var(--radius-sm)] border border-input bg-background px-2 text-sm"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
      </label>
      <button
        className="h-8 rounded-[var(--radius)] bg-primary text-sm font-semibold text-primary-foreground"
        type="button"
        onClick={() => setSaved(email)}
      >
        Save
      </button>
      {saved !== null && (
        <p className="text-xs text-muted-foreground">
          Saved: <span className="font-mono">{saved || "(empty)"}</span>
        </p>
      )}
    </form>
  );
}

/** Chat + page, joined by the copilot. Must sit inside `PageSnapshotProvider`. */
function Wired() {
  const snapshot = usePageSnapshot();
  const fake = useFakeAdapter();
  const copilot = usePageCopilot(fake);

  // The SENT snapshot's registry, never the newest one: CST refs are
  // positional, so a later capture renumbers them and `@e1` would resolve to a
  // different element than the one the agent named.
  const queue = useProposals(snapshot.sentSnapshot?.refs ?? null, copilot.reportResult);

  const renderers = useMemo(
    () => ({
      // Text has no default renderer on purpose — drawing it needs the
      // markdown component from the `./content` subpath, so a read-only host
      // pays nothing for shiki and katex. A host that wants text names it.
      text: ({ part }: PartRenderProps) =>
        part.type === "text" ? <Response>{part.text}</Response> : null,
      // Ours handles `ui-action` and hands every other kind to the chat's own
      // renderer, which is the point of `fallback`.
      data: createActionRenderer({ queue, fallback: DataRenderer }),
    }),
    [queue]
  );

  // Presets rather than a hint to read: the point of the demo is the proposal
  // flow, and remembering which sentence triggers it is not part of that.
  // These send down the same path a typed message does.
  const capabilities = useMemo(
    () => ({
      suggestions: {
        items: [
          {
            id: "fill",
            title: "Fill my email",
            prompt: "fill my email",
          },
          {
            id: "save",
            title: "Save this form",
            prompt: "save this",
          },
        ],
      },
    }),
    []
  );

  return (
    <div className="flex h-[560px] items-stretch gap-6">
      <div className="flex w-[420px] flex-col rounded-[var(--radius)] border border-border">
        <Chat
          adapter={copilot.adapter}
          capabilities={capabilities}
          renderers={renderers}
          // `[]` means LOADED AND EMPTY. Omitting it means "not loaded yet",
          // and starter rows stay hidden — a 90-message room must not open on
          // suggestions while its history is still in flight.
          //
          // Hoisted, NOT inline: a new array identity reseeds the transcript,
          // so an inline `[]` wipes the conversation on every re-render — and
          // settling a proposal is a re-render.
          conversation={EMPTY_ROOM}
          body={{ kind: "packaged" }}
        />
      </div>
      <DemoForm />
    </div>
  );
}

const meta = {
  title: "Widgets/Chat/PageCopilot Live",
  component: Wired,
  tags: ["autodocs"],
  parameters: {
    layout: "padded",
    docs: {
      description: {
        component:
          "A chat that sees the page and proposes actions on it. The adapter is a local fake; the refs it cites come from a real capture of this page.",
      },
    },
  },
} satisfies Meta<typeof Wired>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Live: Story = {
  render: () => (
    <PageSnapshotProvider defaultLinked>
      <Wired />
    </PageSnapshotProvider>
  ),
};
