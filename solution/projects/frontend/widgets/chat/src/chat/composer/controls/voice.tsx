import { ChevronDown, ChevronLeft, ChevronRight } from "lucide-react";
import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";

import { useHotkey, useIsTouch } from "@djangocfg/ui-core/hooks";

import { useChatCopy } from "../../../i18n";
import { useDismiss } from "../../primitives";
import { useCapabilities, useVoice } from "../../store";
import { ComposerButton } from "./button";
import { useComposer } from "../context";
import { LanguageMenu, languageLabel } from "./language-menu";

/** Starts and stops dictation; shown in the mic's tooltip as ⌘⇧D / Ctrl+Shift+D. */
const DICTATE_HOTKEY = "mod+shift+d";

export interface ComposerVoiceProps {
  readonly className?: string;
  /**
   * Icon or glyph. The accessible name comes from the labels, never from this.
   *
   * A FUNCTION of `recording`, matching `ComposerSend` and `ToolCallHeader`: the
   * glyph must change with the role, and a static node cannot express that.
   *
   * Optional, but every assembly we ship passes one — an omitted `children` is
   * how `ComposerSend` renders a blank blue pill. The default in
   * `ui/chat/chat.tsx` exists so a host never has to think about it.
   */
  readonly children?: (recording: boolean) => ReactNode;
  /**
   * The dictation language and how to change it.
   *
   * Absent ⇒ the mic alone, no options button. A host that has no opinion still
   * gets working dictation, because `useSpeechLanguage` resolves a default;
   * passing this is what makes the resolved value VISIBLE and overridable.
   */
  readonly language?: {
    readonly value: string;
    readonly onChange: (tag: string) => void;
  };
}

/**
 * Dictation, or nothing at all.
 *
 * **No engine ⇒ absent button**, never a disabled one — a greyed-out mic is a
 * promise the product cannot keep. Note the threshold is the ENGINE, not the
 * capability: an absent capability falls back to the package's Web Speech
 * default, so only a browser without one yields no button. A host supplying its
 * own capability overrides that default outright.
 *
 * The ANCHOR lives here, not in `VoiceSession`. The session knows only what was
 * dictated; what the user had already typed before pressing the mic is composer
 * state. Without anchoring, dictating into a half-written message replaces it.
 */
export function ComposerVoice({ className, children, language }: ComposerVoiceProps) {
  const { voice: capability, voiceSounds } = useCapabilities();
  const copy = useChatCopy().voice;
  const { draft, setText, onSend } = useComposer();
  const { available, recording, text, start, stop, cancel } = useVoice(
    capability,
    language?.value,
    voiceSounds?.play,
  );
  // A touch device has its own keyboard dictation: a second microphone (and its language picker) is a duplicate tile,
  // whatever the host passes. A desktop keeps both.
  const touch = useIsTouch();
  const [pickerOpen, setPickerOpen] = useState(false);
  // Which view the ONE panel is showing. A view switch rather than a second
  // popover: nesting one floating surface inside another makes both fight over
  // the same outside-press, and the inner search box loses keys to the outer.
  const [view, setView] = useState<"main" | "language">("main");

  const panelRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const close = useCallback(() => {
    setPickerOpen(false);
    // Reset on the way out, so reopening always starts at the top rather than
    // wherever the last visit ended.
    setView("main");
  }, []);

  // The trigger is `inside` too — otherwise its own press dismisses and
  // reopens in one gesture, and the panel can never be closed by its button.
  useDismiss({ open: pickerOpen, onDismiss: close, refs: [panelRef, triggerRef] });

  // Text present when dictation began. A ref, not state: it is read in a
  // handler and an effect, never rendered.
  const anchor = useRef("");
  // Whether THIS session's transcript may write to the draft. Set on press,
  // cleared on the commit, so a settled session cannot keep re-anchoring — see
  // the effect below for the duplication that caused.
  const armed = useRef(false);
  // The draft, readable without depending on it. The click handler needs the
  // CURRENT text, but this button has no reason to re-render on every keystroke.
  const draftText = useRef(draft.text);
  draftText.current = draft.text;

  // A send ends dictation and discards what it heard.
  //
  // `cancel`, never `stop`: stop commits the in-flight interim into a draft the
  // send just cleared, so the sent words reappear in the empty field.
  //
  // `armed` is disarmed here because it lives in this component, not the
  // session: cancel emits one last empty snapshot that an armed effect would
  // write into the new draft.
  //
  // Registered unconditionally — gating on `recording` would re-subscribe once
  // per interim result, and cancel on an idle session is a no-op.
  useEffect(() => {
    return onSend(() => {
      armed.current = false;
      anchor.current = "";
      cancel();
    });
  }, [onSend, cancel]);

  const onClick = useCallback(() => {
    if (recording) {
      stop();
      return;
    }
    // Captured on the way IN, before the session emits anything, so the anchor
    // is the user's typed text and never a previous transcript.
    anchor.current = draftText.current;
    armed.current = true;
    start();
  }, [recording, start, stop]);

  // Push the transcript into the draft as it arrives. Depends on `text`, so an
  // interim REPLACING its predecessor replaces it in the field too — the
  // duplicate-sentence bug `VoiceSession` exists to prevent, preserved across
  // the React boundary rather than re-solved here.
  //
  // Gated on `armed`, NOT on `text !== ""`. The empty-text guard looks
  // equivalent and is not: `start()` emits an empty snapshot, so a settled
  // session's transcript could be re-applied by a later unrelated render, on top
  // of whatever the user had typed since.
  //
  // What this does NOT do is stop a second dictation appending to the first —
  // that is correct behaviour, not duplication. A user who presses the mic twice
  // dictated twice, and the anchor is the draft as it stands, first transcript
  // included.
  useEffect(() => {
    if (!armed.current) return;
    setText(anchor.current === "" ? text : `${anchor.current} ${text}`);
    // Disarm once the session has settled and delivered its final text. Leaving
    // it armed would let a later unrelated render re-apply the same transcript
    // on top of whatever the user has typed since.
    if (!recording && text !== "") armed.current = false;
  }, [recording, text, setText]);

  // The icon already says "dictate", so the hover hint is the shortcut alone.
  // Modifier-bearing, so it works while the caret is in the composer field.
  useHotkey(DICTATE_HOTKEY, onClick, { enabled: available && !touch, preventDefault: true });

  if (!available || touch) return null;

  const micLabel = recording ? copy.stop : copy.start;
  const mic = (
    <ComposerButton
        tooltip={{ content: null, hotkey: DICTATE_HOTKEY }}
        className={className}
        aria-label={micLabel}
        // A toggle, so the state is announced rather than inferred from the icon.
        aria-pressed={recording}
        // The state as DATA, so `styles/composer.css` owns the halo and its
        // reduced-motion fallback. A Tailwind arbitrary variant would need the
        // keyframes declared somewhere anyway, and then the rule and its
        // animation would live in two files.
        data-recording={recording || undefined}
        onClick={onClick}
      >
        {children?.(recording)}
      </ComposerButton>
  );

  if (language === undefined) return mic;

  const back = (
    <div className="border-border flex items-center gap-1 border-b px-1 py-1">
      <button
        type="button"
        aria-label={copy.languageBack}
        onClick={() => setView("main")}
        className="text-muted-foreground hover:bg-accent hover:text-foreground inline-flex h-6 w-6 items-center justify-center rounded-sm"
      >
        <ChevronLeft className="size-4" aria-hidden />
      </button>
      <span className="text-sm font-medium">{copy.languageMenu}</span>
    </div>
  );

  const panel =
    view === "language" ? (
      <LanguageMenu
        current={language.value}
        onSelect={(tag) => {
          language.onChange(tag);
          close();
        }}
        label={copy.languageMenu}
        searchLabel={copy.languageSearch}
        emptyLabel={copy.languageEmpty}
        header={back}
      />
    ) : (
      <div className="flex flex-col gap-0.5 p-1">
        {/*
          The current value is on the ROW, not only behind it. A user whose
          dictation returns nonsense has to be able to read what it is listening
          for at the point where it fails — otherwise the state that broke the
          feature is invisible from the feature.
        */}
        <button
          type="button"
          onClick={() => setView("language")}
          className="hover:bg-accent hover:text-accent-foreground flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-left text-sm"
        >
          <span className="flex min-w-0 flex-1 flex-col">
            <span>{copy.languageMenu}</span>
            <span className="text-muted-foreground truncate text-xs">
              {languageLabel(language.value)}
            </span>
          </span>
          <ChevronRight className="text-muted-foreground size-4 shrink-0" aria-hidden />
        </button>
      </div>
    );

  // Trigger LEFT of the mic, mic last. The mic is the control the user aims for
  // and the one that must stay adjacent to Send; an options button between them
  // makes the action bar read as two competing primary buttons.
  return (
    <span className="relative inline-flex items-center gap-1">
      {/* The shared control, like every other button in this row. Hand-rolled it
          tinted with `--accent` — the theme's highlight, blue here — so this one
          answered a hover with a coloured plate while its neighbours answered
          with a grey one, and the row read as four unrelated controls. */}
      <ComposerButton
          tooltip={copy.language}
          ref={triggerRef}
          aria-label={copy.language}
          aria-expanded={pickerOpen}
          aria-haspopup="dialog"
          onClick={() => {
            setPickerOpen((open) => !open);
            setView("main");
          }}
        >
          <ChevronDown className="size-4" aria-hidden />
        </ComposerButton>
      {pickerOpen ? (
        <div
          ref={panelRef}
          role="dialog"
          aria-label={copy.language}
          /*
            Anchored to the trigger's RIGHT edge, not its left. The panel is
            wider than the control that opens it, so `left-0` sends 256px of it
            off past the composer's right edge — measured as a menu floating
            detached in the middle of the transcript. `right-0` grows it back
            over the composer, which is the only direction with room.
          */
          className="border-border bg-popover text-popover-foreground absolute bottom-full right-0 z-20 mb-2 w-64 overflow-hidden rounded-lg border shadow-lg"
        >
          {panel}
        </div>
      ) : null}
      {mic}
    </span>
  );
}
