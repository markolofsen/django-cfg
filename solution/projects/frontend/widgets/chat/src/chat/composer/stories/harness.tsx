import { CornerDownLeft, Mic, MicOff, Square } from "lucide-react";

import type { ChatCapabilities } from "../../core";
import type { StreamChunk } from "../../core/conversation/chunks";
import { ChatProvider } from "../../store";
import { mockAdapter } from "../../testing";
import { Composer } from "../composer";
import { ComposerQueue } from "../tray/queue";
import { ComposerSend } from "../controls/send";
import { ComposerVoice } from "../controls/voice";
import { Field } from "./field";

/**
 * The composer workbench.
 *
 * Separate from `primitives/stories/harness.tsx` rather than a variant of it:
 * that one auto-sends on mount to produce a transcript, which is the opposite
 * of what these stories need. Here nothing is sent until someone types, because
 * the states worth seeing — a menu tracking the caret, the send button
 * flipping to Stop — only exist while a human is mid-input.
 *
 * Copy is passed in as English literals. This package carries no locales
 * (`ComposerInput`'s `label` is documented as host copy), so a workbench that
 * reached for i18n would be inventing a dependency the components refuse.
 */

const surface = "relative grid gap-2 rounded-lg border border-border bg-background p-2";
// `rounded-control` — ui-core's `--radius-control`, the app's one corner for
// interactive controls. Matches what `ui/chat/chat.tsx` ships, so the workbench and
// the packaged chat cannot drift on geometry.
const sendButton =
  "grid size-8 shrink-0 place-items-center rounded-control bg-primary text-primary-foreground disabled:opacity-40";
// The mic is secondary: same geometry, no fill until it is recording. Filling it
// like Send would give two primary actions and no way to tell which one sends.
const voiceButton =
  "grid size-8 shrink-0 place-items-center rounded-control text-muted-foreground hover:bg-muted aria-pressed:bg-destructive aria-pressed:text-destructive-foreground";
// A row, not two grid children: the buttons share one cell at the end of the
// composer, and `justify-self-end` on each would stack them in the same column.
const toolbar = "flex items-center justify-end gap-1";

export interface ComposerHarnessProps {
  /** Chunks the mock adapter replays once a turn is sent. */
  readonly script?: readonly StreamChunk[];
  readonly delayMs?: number;
  readonly capabilities?: ChatCapabilities;
  /** Seed the ↑ ladder, OLDEST first. It also grows as prompts are sent. */
  readonly history?: readonly string[];
  /** Seed the field, for states that need text without typing. */
  readonly initialText?: string;
  /**
   * Persist the draft under this room, as a host does.
   *
   * Absent ⇒ no persistence, which is every other story: a shared workbench key
   * would let one story's leftover text appear in the next one.
   */
  readonly draftRoom?: string;
  /**
   * Send the seeded text on mount, so a story can PARK mid-turn.
   *
   * Off by default, which is the whole reason this workbench is separate from
   * the transcript one: the composer's states exist while someone is typing,
   * and a harness that always sent would clear the field before any of them
   * could be seen. `Streaming` is the one story that needs the opposite, and a
   * doc comment claiming that state while the button renders idle is only
   * catchable in the browser: every assertion here reads the source rather than
   * the running button.
   */
  readonly sendOnMount?: boolean;
}

export function ComposerHarness({
  script = [],
  delayMs = 40,
  capabilities,
  history,
  initialText,
  draftRoom,
  sendOnMount = false,
}: ComposerHarnessProps) {
  return (
    <ChatProvider
      adapter={mockAdapter({ script, delayMs })}
      capabilities={capabilities}
    >
      <Composer className={surface}>
        <ComposerQueue
          className="rounded border border-border bg-muted/40 px-2 py-1 text-xs"
          itemClassName="flex items-center justify-between gap-2 py-0.5"
        />
        <Field
          history={history}
          initialText={initialText}
          draftRoom={draftRoom}
          sendOnMount={sendOnMount}
        />
        <div className={toolbar}>
          <ComposerVoice className={voiceButton}>
            {(recording) =>
              recording ? (
                <MicOff className="size-4" aria-hidden />
              ) : (
                <Mic className="size-4" aria-hidden />
              )
            }
          </ComposerVoice>
          <ComposerSend className={sendButton}>
            {(streaming) =>
              streaming ? (
                <Square className="size-3.5 fill-current" aria-hidden />
              ) : (
                <CornerDownLeft className="size-4" aria-hidden />
              )
            }
          </ComposerSend>
        </div>
      </Composer>
    </ChatProvider>
  );
}
