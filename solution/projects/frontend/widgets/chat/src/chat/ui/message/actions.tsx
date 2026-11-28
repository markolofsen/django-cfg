import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";

import { cn } from "@djangocfg/ui-core/lib";

import { isOtherParticipant, isTextPart, type ChatMessage } from "../../core/conversation/parts";
import { TooltipHint } from "@djangocfg/ui-core";

/**
 * The per-message action row: the package owns placement, reveal and a11y; the
 * host owns which actions exist. Hence a list of descriptors, not `showRetry` /
 * `showCopy` flags — a flag per feature cannot express an action this package
 * has never heard of, and a host with no retry lane gets a correct one-button
 * row instead of a broken three-button one.
 */

export interface MessageAction {
  /** Stable key. Also the `data-action` value, which is what a story asserts on. */
  readonly id: string;
  /** Accessible name. Required — the row is icon-only, so nothing else names it. */
  readonly label: string;
  readonly icon: ReactNode;
  readonly onSelect: () => void;
  readonly disabled?: boolean;
}

export interface MessageActionsProps {
  readonly message: ChatMessage;
  readonly actions: readonly MessageAction[];
  readonly className?: string;
}

/**
 * In flow and always present, faint until the message is hovered or focused.
 *
 * Not an overlay: a row that floats over the transcript does not read as
 * belonging to the message it acts on. It holds its place instead, and the
 * height it takes is given back by pulling the NEXT message up (`ChatMessage-
 * Frame` sets a negative top margin on the following row), so the transcript
 * keeps the spacing it had before actions existed.
 *
 * Faint rather than invisible: at zero the control cannot be discovered without
 * hovering every message, and a first-time reader never learns it is there.
 * `focus-within` is the keyboard half — hover alone leaves it unreachable.
 */
export function MessageActions({ message, actions, className }: MessageActionsProps) {
  const isUser = message.role === "user" && !isOtherParticipant(message);
  if (actions.length === 0) return null;

  return (
    <div
      role="group"
      aria-label={message.role}
      className={cn(
        "flex h-7 items-center gap-0.5",
        // Aligned with what it acts on: under the reply on the left, under the
        // bubble on the right.
        isUser ? "justify-end" : "justify-start",
        "opacity-10 transition-opacity",
        "group-hover:opacity-100 group-focus-within:opacity-100",
        className,
      )}
    >
      {actions.map((action) => (
        // The design system's tooltip, not the native `title`: the OS bubble
        // ignores the theme, waits ~1s, and would be the one control in the
        // host still using it. `label` doubles as the `aria-label`, which
        // Radix links with `aria-describedby` rather than repeating.
        //
        // A disabled button fires no pointer events; `TooltipHint` wraps it in a span so the name still shows.
        <TooltipHint key={action.id} tooltip={action.label} disabled={action.disabled}>
          <button
            type="button"
            data-action={action.id}
            aria-label={action.label}
            disabled={action.disabled}
            onClick={action.onSelect}
            className={cn(
              "inline-flex h-7 w-7 items-center justify-center rounded-md",
              "text-muted-foreground transition-colors",
              "hover:bg-secondary hover:text-foreground",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              "disabled:pointer-events-none disabled:opacity-50",
            )}
          >
            {action.icon}
          </button>
        </TooltipHint>
      ))}
    </div>
  );
}

/**
 * Text parts only. Reasoning collapses by default and is not the answer a
 * reader means by "copy this"; a tool call's rendered form is not its data, so
 * copying a diff card as JSON is worse than offering nothing.
 */
export function messageCopyText(message: ChatMessage): string {
  return message.parts
    .filter(isTextPart)
    .map((part) => part.text)
    .join("\n\n")
    .trim();
}

export interface UseCopyActionOptions {
  readonly label: string;
  readonly copiedLabel: string;
  readonly icon: ReactNode;
  readonly copiedIcon: ReactNode;
  /**
   * Injected so this package acquires no clipboard implementation. Must return
   * false rather than throw when the write did not land — the confirmed state
   * reads it.
   */
  readonly write: (text: string) => Promise<boolean>;
  /** How long the confirmed state holds, in ms. */
  readonly confirmMs?: number;
}

/**
 * `undefined` when the turn has no text, so a tool-only turn offers no control
 * rather than one that writes an empty string. The icon flips only on a real
 * success — a check after a failed write is a lie the user acts on.
 *
 * Also `undefined` while the turn is still STREAMING. Text length alone was the
 * whole condition, and a streaming turn has text from its first token, so the
 * control appeared over a half-written answer and copied whatever had arrived
 * by the instant of the click. Worse, it appeared over a turn showing only
 * "Thinking" — a reasoning part carries no text, so the row was offering to
 * copy nothing at all.
 *
 * `interrupted` and `failed` DO get the control: both are final, their text is
 * whatever the turn managed to produce, and that is exactly what a reader wants
 * to keep. Only `streaming` is a moving target.
 */
export function useCopyAction(
  message: ChatMessage,
  options: UseCopyActionOptions,
): MessageAction | undefined {
  const { label, copiedLabel, icon, copiedIcon, write, confirmMs = 1500 } = options;
  const [copied, setCopied] = useState(false);
  const text = messageCopyText(message);
  // One timer, cleared on unmount and before rearming: copying twice in quick
  // succession stacked two, and the first cleared the tick while the second
  // copy was still fresh.
  const confirmTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(
    () => () => {
      if (confirmTimerRef.current) clearTimeout(confirmTimerRef.current);
    },
    [],
  );

  const onSelect = useCallback(() => {
    void write(text).then((ok) => {
      if (!ok) return;
      setCopied(true);
      if (confirmTimerRef.current) clearTimeout(confirmTimerRef.current);
      confirmTimerRef.current = setTimeout(() => {
        confirmTimerRef.current = null;
        setCopied(false);
      }, confirmMs);
    });
  }, [write, text, confirmMs]);

  if (text.length === 0) return undefined;
  if (message.status.state === "streaming") return undefined;
  return {
    id: "copy",
    label: copied ? copiedLabel : label,
    icon: copied ? copiedIcon : icon,
    onSelect,
  };
}
