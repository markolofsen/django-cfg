/**
 * Capabilities — the answer to 83 props.
 *
 * Every optional feature is ONE object. Present means the feature exists;
 * absent means it does not, and no UI for it renders. There is no boolean to
 * contradict the object, and no companion props to keep in sync with it — those
 * two failure modes are what produced a configuration space nobody could
 * enumerate (`@rules/architecture.md`).
 *
 * The rule that keeps it honest: a capability owns the WHOLE feature — its
 * behaviour, its limits, its callbacks. If adding one still requires a prop on
 * `<Chat>`, the capability is drawn wrong.
 */

import type { AttachmentsCapability } from "./compose/attachments";
import type { LinksCapability } from "./links/preview";
import type { MentionItem, Person } from "./room/recipient";
import type { MediaBlock, MediaGeneration } from "./media/block";
import type { ToolsCapability } from "./tools/capability";
import type { VoiceSoundsCapability } from "./voice/earcons";

/** One choice in the model switch. `id` is what the host's backend reads (an alias such as `fast`, or a model name); the chat never interprets it. */
export interface ModelOption {
  readonly id: string;
  readonly label: string;
  /** A short second line under the label ("Quick answers"). */
  readonly hint?: string;
}

/**
 * Which model answers. The options and what each id means are the host's data; the value is controlled, so the host can persist it.
 * Present: a small menu in the composer's control row, and the chosen id rides on `SendRequest.model` (only through the chat's own store, not a store the host supplies).
 * Absent: no menu, no `model` on the request.
 */
export interface ModelsCapability {
  readonly options: readonly ModelOption[];
  readonly value: string;
  readonly onChange: (id: string) => void;
}

/**
 * Re-running a turn.
 *
 * Separate from the adapter because not every backend can: a replayed history
 * transcript has no live turn to retry, and the button must be absent there
 * rather than present-and-broken.
 */
export interface RetryCapability {
  readonly retry: (messageId: string) => void;
}

/**
 * End the turn on the AGENT, not just the local stream.
 *
 * Aborting the stream only closes this tab's reader: the run is deliberately
 * detached from its caller, so the agent keeps working and the button silences
 * the tab. This carries the explicit stop the host sends instead.
 *
 * Absent ⇒ Stop stays local-only, which is correct for a host with no transport
 * behind it — a replayed transcript has no run to end.
 */
export interface CancelRunCapability {
  /** Rejects on a refusal the host chose to surface; the abort happens either way. */
  readonly cancel: () => Promise<void>;
}

/**
 * Dictation.
 *
 * The contract is the smallest one that works: start, stop, and a stream of
 * text. Which engine, which language and whether audio leaves the device are
 * product and privacy decisions, and this seam is what keeps them the host's.
 *
 * **Absent does NOT mean no microphone here**, unlike every other capability.
 * The package ships a Web Speech default (`core/voice/web-speech.ts`), so an
 * absent capability falls back to the browser and only a browser without an
 * engine yields no button. A host supplying one overrides the default outright.
 * The exception is deliberate: without it every consumer re-implements the same
 * engine, which is how a host ends up depending on an external toolkit for a
 * seam the package could have owned.
 *
 * `false` is how a host says NO — the one thing absence cannot express here,
 * since absence already means "use the default". A phone keyboard has dictation
 * of its own, so a second microphone in the composer is a duplicate control
 * spending a tile in the row a thumb reaches.
 */
export interface VoiceCapability {
  /**
   * Begin dictation.
   *
   * `onText` may be called many times. `final: false` is an interim result that
   * REPLACES the previous interim; `final: true` commits. Without that
   * distinction an interim "hello wor" and its correction both land in the
   * draft and the user watches their sentence duplicate itself.
   */
  readonly start: (
    onText: (text: string, final: boolean) => void,
    signal: AbortSignal,
  ) => Promise<void>;
  /**
   * Stop and discard any uncommitted interim.
   *
   * MUST be safe to call synchronously from a send. The archived chat notes
   * why: on submit, "voice dictation stops recording instead of talking into a
   * sent message" — a listener that settles asynchronously lets the next words
   * land in a draft that has already been cleared.
   */
  readonly stop: () => void;
}

/**
 * Rendering the agent's media blocks.
 *
 * Absent ⇒ media blocks render NOTHING. That is the safe default rather than a
 * degraded one: a media src is a URL the MODEL chose, and displaying it is an
 * outbound request made on the user's behalf. A host that cannot say which
 * same-origin paths are legitimately its own cannot gate that request, so it
 * must not make it.
 *
 * The prefixes are the capability's whole content because they are the one part
 * a package cannot know. `core/media/allowed-src.ts` gates schemes on its own —
 * `https:`, `app://`, `data:image/` are the same everywhere — but an absolute
 * path is only safe relative to whoever serves the transcript. Baking one
 * transport's routes into this package would be the second source of truth its
 * own header refuses.
 */
export interface MediaCapability {
  /**
   * Absolute-path prefixes this host serves media from, e.g.
   * `/api/admin/attachments/`. Case-sensitive, and matched only after the path
   * is proven already-clean — see `isAllowedSrc`.
   *
   * Empty ⇒ only the allowlisted SCHEMES render; no same-origin path does.
   */
  readonly sameOriginPrefixes: readonly string[];
  /**
   * Draw a playable block (audio, video, map) with the host's own player.
   *
   * Absent ⇒ the native `<audio controls>` / `<video controls>`, which cannot
   * join the shell's player, show embedded artwork, or rewrite a video src
   * onto a streaming route.
   *
   * On MediaCapability rather than its own: a host that can render media is the
   * same host that decides what a player is. Returning undefined for one kind
   * falls back per kind.
   *
   * `unknown`, not `ReactNode`: `src/core` imports no React. The renderer that
   * consumes this narrows it.
   */
  readonly renderPlayer?: (block: MediaBlock) => unknown;
  /**
   * Draw a picture with the host's own viewer.
   *
   * Absent ⇒ a plain `<img>`, which is the one thing in a transcript that looks
   * openable and is not. The seam exists for the same reason `renderPlayer`
   * does: a lightbox is a heavy dependency belonging to the host's design
   * system, and a package that shipped one would carry it into every mount.
   *
   * Format is never part of the decision — whatever the browser can render,
   * the host is handed the same src the `<img>` would have used.
   * `unknown`, not `ReactNode`: `src/core` imports no React.
   */
  readonly renderImage?: (image: {
    readonly src: string;
    /** The filename, which is also the picture's only description. */
    readonly title: string;
    /** What produced it, when a tool authored the picture rather than found it. */
    readonly generation?: MediaGeneration;
  }) => unknown;
}

/**
 * Starter prompts for an empty room.
 *
 * Absent ⇒ an empty transcript shows its one line of text and nothing else, the
 * same absent-not-stubbed rule as voice. A read-only replay has no agent to
 * start, so the affordance must be absent rather than inert.
 *
 * The CATALOGUE is the host's, and that is load-bearing rather than tidy:
 * choosing the set needs facts this package cannot hold — which of the agent's
 * tool families exist on the server behind the transport, and that different
 * agent engines reach different subsets of them. A list declared here would be
 * a second source of truth against the one the host generates.
 *
 * The stakes are higher than for a menu of verbs the transport can refuse. An
 * unsupported verb comes back as an error; a suggestion is ordinary prose, so
 * nothing refuses it — the model answers, improvising about a tool it does not
 * have. There is no server-side gate behind this list at all.
 */
export interface SuggestionsCapability {
  /** The list to offer, already filtered by the host, in display order. */
  readonly items: readonly ChatSuggestion[];
  /**
   * The language to answer in, named in ENGLISH ("Russian"), appended to the
   * prompt as one sentence.
   *
   * Prompts stay English because they are model-facing; the reply is what the
   * user reads. The host supplies it: no locale reaches the agent on the ask
   * path, so this cannot be decided further down.
   *
   * Absent ⇒ nothing appended. An English-language host needs no "Reply in
   * English."
   */
  readonly replyLanguage?: string;
  /**
   * Observe a pick. The prompt is ALREADY SENT when this runs — this is a
   * notification, not the send itself.
   *
   * The package sends it down the same path the composer uses (`store.send`),
   * which is what makes a picked row indistinguishable from a typed message:
   * it queues behind a turn in flight, it gets the same optimistic row, and it
   * obeys the same guards. A host performing the send itself would be a second
   * path to one behaviour, and the two would drift on exactly those cases.
   */
  readonly onPick?: (suggestion: ChatSuggestion) => void;
}

/**
 * One starter row.
 *
 * Two texts, deliberately, because two audiences read them: `title` is shown
 * and translated, `prompt` is sent to the model and is not. One string used as
 * both — the shape Vercel's primitive takes — forces a choice between a row too
 * long to scan and a prompt too terse to act on.
 */
export interface ChatSuggestion {
  readonly id: string;
  /** What the row READS. Short enough for a narrow pane. */
  readonly title: string;
  /** What is SENT. May be much longer than the title. */
  readonly prompt: string;
  /**
   * Glyph KEY, never a node — the catalogue crosses the transport as data. An
   * unmapped key draws no glyph rather than failing, so a row may ship before
   * its icon.
   */
  readonly icon?: string;
}

/**
 * Reading back a mention the composer wrote as an opaque token.
 *
 * Absent ⇒ every mention already reads as itself, which is true wherever the
 * written token IS the name. A host whose correspondents are named in free text
 * writes an id instead — that is what keeps a mention resolvable and durable
 * across a rename — and supplies this so the reader still sees the name.
 *
 * An unknown token resolves to nothing and stays as written. It names someone
 * who has left or has not loaded, and a substituted guess would put a wrong
 * name into a message already sent.
 */
export interface MentionNamesCapability {
  readonly nameFor: (token: string) => string | undefined;
  /**
   * The whole correspondent behind a token, for a host that draws more than a
   * name — a face, a role, a card.
   *
   * `unknown`, not a typed row: `src/core` imports no React and knows nothing
   * about what a correspondent IS. The host that supplies this is the same one
   * that renders it, so the type is checked where both ends meet rather than
   * described here. Absent ⇒ the name alone.
   */
  readonly contactFor?: (token: string) => unknown;
  /**
   * How to WRITE a mention of this address, already serialized.
   *
   * The finished text rather than its parts, because the spelling belongs to
   * the host that owns how a mention is written — returning the parts would let
   * a second caller compose them differently. Absent ⇒ no way to write one, and
   * the affordance is omitted.
   */
  readonly mentionFor?: (token: string) => string | undefined;
}

/**
 * The `@` menu of a room: the names a message can mention.
 *
 * Absent ⇒ typing `@` opens nothing. The items are the host's because only it
 * knows the roster and the words in the reader's language; the package decides
 * nothing about who is in the room. A mention is text: it does not choose who
 * reads the line (that is the recipient chip).
 */
export interface MentionsCapability {
  /** The assistant first, people after. Choosing a row writes its name into the text and nothing else. */
  readonly items: readonly MentionItem[];
}

/**
 * Who a line can be written to privately: the recipient chip above the field.
 *
 * Absent ⇒ no chip and every line is for the room. The host passes the people it may write to (this seat and the assistant
 * already left out: the assistant is never a recipient) and the words, because only it knows the roster and the language.
 */
export interface RecipientsCapability {
  readonly people: readonly Person[];
  /** The field's placeholder while a private recipient is chosen. */
  readonly placeholderFor: (person: Person) => string;
}

/**
 * Names for the `authorId` a message carries.
 *
 * Absent, or `undefined` for an id ⇒ that turn wears no speaker line. The host
 * leaves its own seat out, so a sender's bubbles are not captioned "You".
 */
export interface AuthorsCapability {
  readonly labelFor: (authorId: string) => string | undefined;
}

/**
 * A longer reasoning pass before the answer — the composer's "Think" toggle.
 *
 * Absent ⇒ no button renders. That is the required shape here, not a
 * preference: only a third of the catalogue accepts the `reasoning_effort`
 * request field (measured 2026-08-29 — 133 of 396 models, a strict subset of
 * the 270 that reason), so a toggle shown unconditionally would be pressable
 * and inert on models like Claude Opus and DeepSeek R1. A control that silently
 * does nothing is worse than one that is not there.
 *
 * The host owns the decision because only it can see which model is active —
 * the model catalogue it fetches is what carries `reasoningEffort` per model.
 */
export interface ThinkCapability {
  /**
   * Whether the toggle is currently on. STICKY across turns, like ChatGPT's:
   * it lives with the host, not in the draft, because the draft is cleared on
   * every send and a value stored there would silently switch itself off.
   */
  readonly enabled: boolean;
  readonly setEnabled: (enabled: boolean) => void;
}

/** The events the chat plays a sound for. */
export type ChatSoundEvent = "messageSent" | "messageReceived" | "streamStart" | "error";

/**
 * The message sounds. Absent means ON with the bundled sounds; `false` means silent. Everything here is optional tuning.
 */
export interface ChatSoundsCapability {
  /** 0..1, on top of each event's own level. Default 1. */
  readonly volume?: number;
  /** Mute without removing the capability (a host's own "sound off" switch). */
  readonly muted?: boolean;
  /** Replace the sound of an event with a URL (a data URL works), or `false` to silence that event alone. */
  readonly urls?: Partial<Record<ChatSoundEvent, string | false>>;
}

export interface ChatCapabilities {
  readonly suggestions?: SuggestionsCapability;
  readonly tools?: ToolsCapability;
  readonly retry?: RetryCapability;
  readonly cancelRun?: CancelRunCapability;
  readonly voice?: VoiceCapability | false;
  readonly voiceSounds?: VoiceSoundsCapability;
  /** Message sounds (sent, answer starts, answer done, error). On by default; `false` silences them. */
  readonly sounds?: ChatSoundsCapability | false;
  readonly think?: ThinkCapability;
  readonly media?: MediaCapability;
  readonly mentionNames?: MentionNamesCapability;
  /** The room's `@` menu. See {@link MentionsCapability}. */
  readonly mentions?: MentionsCapability;
  /** The recipient chip. See {@link RecipientsCapability}. */
  readonly recipients?: RecipientsCapability;
  /** Speaker names for a room's header line. See {@link AuthorsCapability}. */
  readonly authors?: AuthorsCapability;
  /** A title and icon for a bare link. See {@link LinksCapability}. */
  readonly links?: LinksCapability;
  /** Attach files to a turn. See {@link AttachmentsCapability}. Absent: no button, no drop, no paste. */
  readonly attachments?: AttachmentsCapability;
  readonly models?: ModelsCapability;
}
