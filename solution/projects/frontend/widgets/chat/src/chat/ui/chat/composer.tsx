import { Brain, CornerDownLeft, Mic, Paperclip, Plus, Square, type LucideProps } from "lucide-react";
import type { ReactNode } from "react";

import {
  Composer,
  ComposerAttach,
  ComposerModel,
  ComposerAttachments,
  ComposerField,
  ComposerPickedTools,
  ComposerQueue,
  ComposerSend,
  ComposerThink,
  ComposerTools,
  ComposerVoice,
  useDraftPersistence,
  type AskReplace,
} from "../../composer";
import { ChatRecipientChip } from "../chips/recipient-chip";
import { ChatReplyChip } from "../chips/reply-chip";
import { ChatSuggestions } from "./suggestions";

export interface ChatComposerProps {
  /** Sent prompts for ↑ recall, OLDEST first. Empty ⇒ the arrows never navigate. */
  readonly history?: readonly string[];
  /** The dictation language, when the host offers a picker. */
  readonly speechLanguage?: {
    readonly value: string;
    readonly onChange: (language: string) => void;
  };
  /**
   * Asked before a queued prompt interrupts the running turn.
   *
   * Passed through to `ComposerQueue`; the package acquires no dialog of its
   * own. Absent ⇒ no interrupt control at all, because an unconfirmed one is
   * the shape this must never ship.
   */
  readonly confirmSendQueuedNow?: () => Promise<boolean>;
  /**
   * Asked before a prompt taken back for editing overwrites a draft in progress.
   *
   * Three outcomes, not a confirm: "keep what I typed" and "keep both" are
   * different answers, and a two-button dialog makes them the same one. Absent ⇒
   * the take replaces the draft outright.
   */
  readonly askReplaceDraft?: AskReplace;
  /**
   * Room identity, to keep an unsent draft across a reload.
   *
   * Absent ⇒ no persistence, and the draft dies with the mount. The VALUE is
   * the host's because this package has no notion of a room; two rooms given
   * one string share a draft, which nothing here can detect.
   */
  readonly draftRoom?: string;
  /** Extra controls, between the field and the mic. */
  readonly toolbarEnd?: ReactNode;
  /**
   * Room-wide surfaces that belong ABOVE the field, inside the same column.
   *
   * An allowance banner and the agent's question describe the ROOM, not the
   * draft, so they sit outside the box — but within the column and its
   * positioning context, because a card that floats `bottom-full` grows upward
   * from this slot's top edge. A host rendering them as a sibling of `<Chat>`
   * puts them outside the reading column, at a different width from the
   * conversation they belong to.
   */
  readonly above?: ReactNode;
  /**
   * Icon KEY → glyph for the empty room's starter rows.
   *
   * The host's, because the catalogue names glyphs as DATA — it crosses Go→TS
   * and can name a picture but cannot be one — and this package ships no icon
   * library. Absent, or an unmapped key, draws no glyph and the row still works.
   */
  readonly suggestionIcon?: (key: string) => ReactNode;
  /**
   * Icon KEY → glyph for a row in the `+` arsenal menu. Same seam, same reason.
   */
  readonly toolIcon?: (key: string) => ReactNode;
  /**
   * The heading for a tool CATEGORY key. Absent ⇒ the registry's raw key.
   *
   * The host's, because the keys are Go's (`stt`, `web`, `disk`) and their
   * translations belong beside the catalogue that mints them: a mapping in this
   * package would go stale the moment a new tool family is registered, and go
   * stale SILENTLY — an unmapped key still renders.
   */
  readonly toolCategoryLabel?: (category: string) => string;
  /** Field on top, controls always on their own row beneath (the Notion arrangement). Absent: the controls share the field's row while the draft is short. */
  readonly stacked?: boolean;
  /** The phone-sized composer: one row of field and send, no `+`, think or microphone, a 44px target, no ring; Enter is a newline on touch. */
  readonly compact?: boolean;
  readonly className?: string;
}

/**
 * Mounts the persistence effects, which need the draft from context. A component
 * rather than a call in `ChatComposer`, because that body sits OUTSIDE
 * `<Composer>` and `useComposer()` throws there. Renders nothing.
 */
function DraftPersistence({ room }: { readonly room: string | undefined }) {
  useDraftPersistence(room);
  return null;
}

/**
 * The composer, assembled.
 *
 * ONE assembly, so a surface cannot silently ship without the queue or the
 * controls beside it — each of which was built, exported, and then left
 * unrendered by a host that composed the parts by hand.
 *
 * The layout AND the copy are the package's; what a host varies is capabilities
 * and data. Copy was the host's until adding one label proved to be a four-file
 * change, and until a host assembled a translated string into a DOM selector —
 * which broke the caret in one locale with types and tests green.
 *
 * `flex-wrap` with `items-end` rather than a measured grid: the controls share
 * the field's row while the draft is short and wrap beneath it when it grows,
 * which is layout doing the work with no measurement, no state and no frame lag.
 */
export function ChatComposer({
  history = [],
  speechLanguage,
  confirmSendQueuedNow,
  askReplaceDraft,
  draftRoom,
  toolbarEnd,
  above,
  suggestionIcon,
  toolIcon,
  toolCategoryLabel,
  stacked = false,
  compact = false,
  className,
}: ChatComposerProps) {
  return (
    /*
      The reading column and the positioning context, both owned HERE.

      `chat-column` caps and centres each child so the composer and the
      transcript agree on where the conversation is; the stylesheet used to ask
      the HOST to put the same class on its own wrapper, which is a rule a host
      can only forget silently — the two surfaces then sit at different widths
      with nothing failing. `relative` anchors an ask card that grows upward
      from this element's top edge (`bottom-full`); without a positioned
      ancestor it resolves against the viewport and lands away from the
      conversation it answers.

      `pr-4` matches the padding the host drops on its right edge so the
      transcript's scrollbar can reach the pane. Here rather than there because
      only this element knows it is the composer's outer box.
    */
    <div className={`chat-column chat-inset-r relative${stacked ? " pt-3" : ""}`} data-touch-newline={compact ? "" : undefined}>
      {above}
      {/*
        Part of the assembly, not a host slot — the same reason `ComposerQueue`
        is: a surface composing this by hand ships without whichever piece it
        forgot, and nothing fails. It is self-gating, so it costs every other
        room one null. ABOVE the box because it describes the ROOM; the reply
        chip sits inside it because it describes the DRAFT.
      */}
      <ChatSuggestions icon={suggestionIcon} />
      <Composer
      before={<ComposerAttachments />}
      /*
        Radius and inset are NOT here. They are one measurement, not two: the
        outer radius has to equal the controls' plus the inset or the corners
        stop running parallel, and a Tailwind pair states them as unrelated
        numbers that drift apart on the next edit. `composer-box` derives one
        from the other in the chat stylesheet, which also carries the
        `:has(textarea[data-multiline])` rule — a selector that looks DOWN at a
        descendant and acts on a different child, legible as CSS and unreadable
        as a class list.
      */
      className={`composer-box ${stacked ? "composer-stacked " : ""}${compact ? "composer-compact " : ""}flex cursor-text flex-wrap items-end gap-2 border border-border bg-background focus-within:border-ring ${className ?? ""}`}
    >
      <DraftPersistence room={draftRoom} />
      <ChatReplyChip />
      {/* Who the line is for: the room, or one person. Absent when there is nobody to write to. */}
      <ChatRecipientChip />
      {/* Absent when empty. `w-full`: it describes the whole draft, not the field. */}
      <ComposerQueue
        confirmSendNow={confirmSendQueuedNow}
        askReplace={askReplaceDraft}
        className="w-full"
        listClassName="flex flex-col gap-1"
        // One class, styled in `styles/composer.css`. The row addresses its
        // children by `data-action`, which a Tailwind arbitrary variant can only
        // express as a quoted selector repeated per property — where a misplaced
        // bracket reads as ordinary noise.
        itemClassName="queued-row"
      />
      {/* BEFORE the field. `composer-lead` (styles/composer.css) sends it down with the other controls on a wrapped draft. A `+`, not a wrench: an icon naming a tool names the wrong one. */}
      {compact ? null : (
      <div className="composer-lead order-1 flex min-w-0 shrink-0 items-center gap-1">
        <ComposerTools icon={toolIcon} categoryLabel={toolCategoryLabel}>
          <Plus className="size-4" aria-hidden />
        </ComposerTools>
        {/* Directly after the `+` that staged them, so a pick lands where the
            user clicked. `min-w-0` lets it shrink rather than push the field
            off the line; `tool-chips` carries the fades and hidden scrollbar. */}
        <ComposerPickedTools
          icon={toolIcon}
          className="tool-chips flex min-w-0 gap-1 overflow-x-auto empty:hidden"
          chipClassName="tool-chip"
        />
      </div>
      )}
      <ComposerField
        /*
          `min-w-[60%]` on the WRAPPER, which is the element flex lays out.
          Measured: without it the field held 83% of the composer and STOPPED —
          a four-line draft wrapped inside 634px while 134px sat empty to its
          right, because the controls never left the row for it to claim.
        */
        wrapperClassName="order-2 min-w-[60%]"
        /*
          `w-full`, NOT `flex-1`: the flex item is the positioned wrapper that
          anchors the mention menu, and the textarea inside it is an ordinary
          block, so `flex-1` here resolves against nothing and the box keeps a
          textarea's intrinsic `cols` width.

          The field reads at the TRANSCRIPT's size, from the same token. What
          you type and what comes back are one conversation; two scales would
          say otherwise.
        */
        /*
          `pt-[3px] pb-[5px]`, not `py-1`: an OPTICAL correction, and the 8px
          total is unchanged so the field still matches the 32px buttons beside
          it. SF Pro's metrics are asymmetric — 10px ascent against 2px descent —
          and a line box centres on those, not on cap height, so symmetric
          padding rendered 10px of air above the glyphs and 7px below. Measured
          by scanning the rendered ink, which is the only thing that sees this:
          every box in the row already measured identical and bottom-aligned.
        */
        className="w-full resize-none bg-transparent pt-[3px] pb-[5px] text-[length:var(--chat-text)] leading-[var(--chat-leading)] outline-none placeholder:text-muted-foreground"
        history={history}
      />
      {/*
        The trailing controls; `+` leads the row rather than sitting here.
        `flex-1`, not `w-full`: this SHARES the line with `+` while claiming the
        rest of it, which keeps the send button at the far edge in both states.
      */}
      <div className="composer-controls order-3 flex flex-1 items-center gap-1">
        {/*
          `ml-auto` rather than `justify-end` on the row: `+` holds the left
          edge, so the row cannot end-align as a whole — this group has to push
          itself right against whatever leads it.
        */}
        <div className="ml-auto flex shrink-0 items-center gap-1">
          {/* Anything a host puts here MUST render `ComposerButton`, including a
              menu or popover trigger, which wraps it. These controls belong to
              three packages and that component is the one place they agree on
              size, radius and hover; `wide` is the variant that carries text. */}
          {toolbarEnd}
          {compact ? null : <ComposerModel />}
          <ComposerAttach>
            <Paperclip className="size-4" aria-hidden />
          </ComposerAttach>
          {/* Renders nothing without a `think` capability. Only a third of the
              catalogue accepts the request field behind it, so the host decides
              per active model — an always-present toggle would be inert on the
              rest, which reads as broken rather than unavailable. */}
          {compact ? null : <ComposerThink className="aria-pressed:text-primary">{() => <Brain className="size-4" aria-hidden />}</ComposerThink>}
          {/* Size, radius, hover and focus come from `ComposerButton`, which both
              of these render.

              Renders nothing without a `voice` capability — the host decides
              whether a microphone exists at all.

              `composer-mic` carries the whole recording appearance — the tumbling
              glyph, the ring, and the red that must outrank hover. All three live
              in `styles/composer.css`: an `aria-pressed:` utility ties with the
              button's own `hover:text-foreground` on specificity, so source order
              decided the colour and the glyph went white under the pointer. */}
          {compact ? null : (
            <ComposerVoice className="composer-mic" language={speechLanguage}>
              {(recording) => (recording ? <StopGlyph /> : <Mic className="size-4" aria-hidden />)}
            </ComposerVoice>
          )}
          {/* A GLYPH is required. Without children this renders an empty pill — a
              button with no affordance and no indication that a turn can be
              stopped. */}
          <ComposerSend className={compact ? "composer-send" : undefined}>
            {(streaming) =>
              streaming ? <StopGlyph /> : <CornerDownLeft className="size-4" aria-hidden />
            }
          </ComposerSend>
        </div>
      </div>
      </Composer>
    </div>
  );
}

/** Filled, so "stop" reads as a state rather than an outline among outlines. */
function StopGlyph(props: LucideProps) {
  return <Square className="size-3.5 fill-current" aria-hidden {...props} />;
}
