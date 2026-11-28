/**
 * The chat package's copy schema.
 *
 * English is the schema of record: every locale dictionary is typed against
 * `ChatCopy`, so a missing or misspelled key fails `tsc` rather than rendering
 * `undefined` into a composer button.
 *
 * Typing is what replaces the shared locale gates. The four scripts under
 * `packages/i18n/scripts/` walk the catalogue in `packages/i18n/src/locales/`
 * and cannot see a package-local dictionary, exactly as they cannot see the
 * onboarding one.
 */

import type { PluralCopy } from "@djangocfg/i18n/copy";

export type { PluralCopy };

/** Copy for the transcript: the log, its empty state, and the wait. */
export interface TranscriptCopy {
  /** Shown when there are no messages — an empty transcript is a real state. */
  readonly empty: string;
  /**
   * Accessible name of the starter-prompt list, so the group is not anonymous.
   *
   * Only the NAME lives here. The rows' own titles come from the host with its
   * catalogue, because what an agent can be asked to do is a fact about the
   * agent and this package does not hold it.
   */
  readonly suggestionsLabel: string;
  /** Accessible name of the log, so the landmark is not anonymous. */
  readonly log: string;
  /** The two strings a screen reader hears per turn. */
  readonly announceStreaming: string;
  readonly announceComplete: string;
  /** The return-to-bottom control, which is icon-only. */
  readonly jumpToLatest: string;
  /** What the wait is for, before the first token arrives. */
  readonly thinking: string;
  /** The elapsed counter. `{{seconds}}` is whole seconds. */
  readonly thinkingElapsed: string;
  /**
   * The two relative day headings. Older days are named by their date, which
   * `lib-utils` formats in the reader's locale — so there is no third key here.
   */
  readonly today: string;
  readonly yesterday: string;
}

/** Copy for the message action row and the collapsible reasoning block. */
export interface MessageCopy {
  readonly copy: string;
  readonly copied: string;
  readonly reply: string;
  /** Copy a link that reopens this one message. */
  readonly copyLink: string;
  /** Confirmation after {@link copyLink}, distinct from `copied`: two actions
   *  in one row both confirm, and one word for both hides which fired. */
  readonly copiedLink: string;
  /** Names the quote above a turn, which is a button back to what it answers. */
  readonly jumpToQuoted: string;
  /** Summary of the collapsed reasoning block, once the thought has settled. */
  readonly reasoning: string;
  /**
   * Summary WHILE the thought is still arriving.
   *
   * A separate key rather than reusing `reasoning`: a block that says
   * "Reasoning" while it fills and "Reasoning" when it is done tells the reader
   * nothing about which state they are looking at, and the live one is the
   * state that explains why nothing else has appeared yet.
   */
  readonly reasoningLive: string;
  /**
   * The block's summary when the engine stripped the words and reported only a
   * count. `{{count}}` is reasoning tokens.
   *
   * This exists because the alternative is silence: a provider that ships the
   * thinking block with its text removed leaves the figure as the only true
   * thing, and a block keyed on text alone renders nothing at all.
   *
   * A `PluralCopy` because it counts: Russian and Polish select a different
   * form at 1, 2 and 5, and a flat string would read as broken grammar on the
   * majority of counts rather than on an edge case.
   */
  readonly reasoningTokens: PluralCopy;
  /**
   * The two labels of the trigger that opens and closes a long turn.
   *
   * Both are present because the control is a toggle whose label states what
   * the next press DOES, not what the current state is — an unlabelled arrow
   * would leave the reader guessing which direction it goes.
   */
  readonly showMore: string;
  readonly showLess: string;
}

/**
 * The four tool-call states, in the order they occur.
 *
 * Named for what the user sees rather than for the wire's `input-streaming`
 * spelling: the vocabulary a person reads is not the vocabulary a protocol
 * uses, and tying the copy to the second makes a protocol rename a copy change.
 */
export interface ToolCopy {
  readonly inputStreaming: string;
  readonly inputAvailable: string;
  readonly outputAvailable: string;
  readonly outputError: string;
  /** Names the disclosure button while the call is open. */
  readonly collapse: string;
  /** Names it while the call is shut. The chevron is decorative, so this is
   *  the only thing a screen reader has to go on. */
  readonly expand: string;
  /**
   * A call the turn ended before it answered (Stop, a lost stream). Not "Failed":
   * nothing went wrong with the tool that is known.
   */
  readonly cancelled: string;
  /** The counter settled successful calls fold into. `{{count}}`. */
  readonly used: PluralCopy;
}

/** The statuses a step can be in, as words. */
export type RunStatusWord = "running" | "ok" | "error" | "timeout" | "skipped" | "cancelled" | "denied" | "pending";
/** The kinds of step that have a generic word (a step with no title of its own is called by it). */
export type RunKindWord = "model" | "reasoning" | "tool" | "approval" | "handoff" | "guardrail" | "source" | "error" | "usage" | "note";

/** Copy for the Run block: what the answer did, as a summary line and a timeline. */
export type RunVerbWord = "read" | "search" | "write" | "other" | "think";

/** One verb phrase, settled and while it runs. */
export interface RunVerbCopy {
  readonly done: string;
  readonly live: string;
}

export interface RunCopy {
  /** Names the timeline for a screen reader. */
  readonly label: string;
  readonly working: string;
  /** The settled header: "Worked for 10s". `{{time}}`. */
  readonly worked: string;
  /** The settled header when the server sent no timing. */
  readonly done: string;
  /** A step with no server wording: a phrase per kind of work. `{{object}}` is what it touched (a source's title, else the tool's name); `think` has none. */
  readonly verb: Readonly<Record<RunVerbWord, RunVerbCopy>>;
  /** The running counter beside the live step. `{{count}}`. */
  readonly tools: PluralCopy;
  /** A count of failed steps. `{{count}}`. */
  readonly failed: string;
  readonly show: string;
  readonly hide: string;
  readonly stepShow: string;
  readonly stepHide: string;
  readonly status: Readonly<Record<RunStatusWord, string>>;
  readonly kind: Readonly<Record<RunKindWord, string>>;
  readonly arguments: string;
  readonly result: string;
  readonly sources: string;
  readonly purpose: string;
  readonly query: string;
  /** `{{input}}` and `{{output}}`. */
  readonly tokens: string;
  /** The server held this step's details back. */
  readonly notShared: string;
  readonly masked: string;
  readonly truncated: string;
  readonly retryable: string;
  readonly copy: string;
  readonly copied: string;
  /** `{{count}}`. */
  readonly more: string;
  /** Settled steps folded past the cap. `{{count}}`. */
  readonly earlier: string;
  /** Steps the server dropped from the stored record. `{{count}}`. */
  readonly omitted: string;
}

/** Copy for the strip of prompts waiting for the current turn to end. */
export interface QueueCopy {
  /** The summary line above a collapsed queue. `{{count}}`. */
  readonly prompts: PluralCopy;
  /** The fold: how many rows are hidden past the inline limit. `{{count}}`. */
  readonly more: PluralCopy;
  /** Folds them back. */
  readonly showLess: string;
  readonly remove: string;
  readonly show: string;
  /** Takes the prompt back into the composer. Tooltip only — the row IS the control. */
  readonly edit: string;
  /**
   * Names the control that cuts the running turn short to release one prompt.
   *
   * Must name BOTH halves — the turn is lost, and a label reading only "send"
   * hides that from the one click where it matters.
   */
  readonly sendNow: string;
  /**
   * The SAME control with no turn to cut short — after a Stop, where the queue
   * refuses to drain on its own.
   *
   * A separate string rather than reusing {@link sendNow}, whose whole job is to
   * name the interruption: promising to stop a reply that already ended
   * describes something that cannot happen, and a label that over-warns is
   * trusted no more than one that under-warns.
   */
  readonly send: string;
  /** The confirmation that guards it. Destructive: work already done is lost. */
  readonly sendNowConfirmTitle: string;
  readonly sendNowConfirmMessage: string;
  /**
   * Asked when taking a prompt back would overwrite what is already typed.
   * The buttons are the dialog's own — only the question is ours.
   */
  readonly replaceDraftTitle: string;
  readonly replaceDraftMessage: string;
}

/** Copy for dictation: the mic, and the language picker beside it. */
export interface VoiceCopy {
  readonly start: string;
  readonly stop: string;
  readonly language: string;
  readonly languageMenu: string;
  readonly languageSearch: string;
  readonly languageEmpty: string;
  readonly languageBack: string;
}

/** Copy for the composer's field, its tools menu, and the send control. */
export interface ComposerCopy {
  /** Accessible name of the textarea. */
  readonly input: string;
  readonly placeholder: string;
  readonly send: string;
  /**
   * Hover-only hint naming the key that sends, beneath the send label.
   *
   * A hint, never the accessible name: it states the binding `field/keys.ts`
   * actually makes — bare Enter — so it must be re-read there before it is
   * changed here, and it stays out of `send` so a screen reader is not read a
   * keyboard tip it cannot act on.
   */
  readonly sendShortcut: string;
  readonly stop: string;
  /** Dismiss the chip naming the message this draft answers. */
  readonly replyClear: string;
  /**
   * The `+` menu: what this agent can do.
   *
   * Names the ARSENAL, not the button's shape. "Add" or "Attach" is what a `+`
   * means in every other chat product, and this one lists capabilities — a
   * label borrowed from the familiar gesture would promise a file picker.
   */
  readonly toolsMenu: string;
  readonly toolsSearch: string;
  readonly toolsEmpty: string;
  /** Heading for the tools this user reached for last, above the catalogue. */
  readonly toolsRecent: string;
  /** Drop one tool from that history: the row's `x`, not the chip's. */
  readonly toolsForget: string;
  /** Drop a picked tool from the draft: the chip's `x`. */
  readonly toolRemove: string;
  /**
   * The field's placeholder while a picked tool still lacks its object.
   *
   * It REPLACES the ordinary placeholder rather than adding a line, so the
   * composer stays one box: the standing advice ("Ask anything") is exactly
   * what stops applying the moment a pick names something more specific.
   *
   * Both are imperative and name the act, never the tool — the chip beside the
   * field already says which tool asked.
   */
  readonly needsFile: string;
  readonly needsSkill: string;
  /**
   * Names the ROW OF CHIPS already picked, not the menu that picks them.
   * Each tool name renders twice — once in `toolsMenu`, once on its chip — so
   * this label must not echo `toolsMenu`, or a screen reader and a test lose
   * the only handle telling the two places apart.
   */
  readonly toolsPicked: string;
  /**
   * Turn the longer-reasoning pass ON — the label while it is off.
   *
   * It NAMES THE COST ("slower, costs more") because this is the only surface
   * that can: the package ships no tooltip, and the button is the last thing a
   * user touches before spending. A bare "Think longer" sells the upside and
   * hides the bill.
   *
   * **Never put a currency amount here.** Money beside the message box is what
   * makes people ration — the same reason the allowance indicator is a bar with
   * no numbers, and amounts live on the review surface (Settings > Plan). State
   * the DIRECTION, never the figure.
   */
  readonly thinkOn: string;
  /** Turn it OFF — the label while it is on. No cost note: stopping costs nothing. */
  readonly thinkOff: string;
  /** The attach button (and its hover name), and the name of the row of files on the draft. */
  readonly attach: string;
  readonly attachments: string;
  /** Drop one file from the draft: the chip's `x`. */
  readonly attachRemove: string;
  /** Why a chip is red: a kind the host did not enable, over the size limit, past the count, or the host's upload failing without a message of its own. */
  readonly attachTypeRefused: string;
  readonly attachTooLarge: string;
  readonly attachTooMany: string;
  readonly attachFailed: string;
  /** The label of the drop zone while files are dragged over the composer. */
  readonly attachDrop: string;
  /** Accessible name and tooltip of the model switch (`capabilities.models`). */
  readonly model: string;
}

/**
 * Words of a multi-participant chat (a call, a team room): the `@` menu, the recipient chip, the speaker line and the
 * copy control beside a link. A one-to-one chat never shows most of them; they are always written so a host needs no
 * extra dictionary.
 */
export interface RoomCopy {
  /** Accessible name of the `@` menu. */
  readonly mentionMenu: string;
  /** The assistant as a mention, and the line under it. */
  readonly assistant: string;
  readonly assistantHint: string;
  /** The recipient chip: "To: Everyone" / "To: Anna". */
  readonly to: string;
  readonly everyone: string;
  readonly everyoneHint: string;
  /** The line under a person in the recipient list. */
  readonly privateHint: string;
  /** The chip's spoken word for a private recipient. */
  readonly privateLine: string;
  /** The chip's accessible name: it opens the list of people. */
  readonly pickRecipient: string;
  /** Speaker line for the reader's own turns, for a host that wants one. */
  readonly you: string;
  /** The copy control next to a link in a message, and its confirmation. */
  readonly copyLink: string;
  readonly linkCopied: string;
  /** Said with a link's title in its tooltip: a web link leaves this page. */
  readonly opensInNewTab: string;
}

/** Copy for the interactive blocks an answer can carry (`blocks/`). */
export interface BlocksCopy {
  readonly apply: string;
  readonly dismiss: string;
  readonly applied: string;
  readonly dismissed: string;
  /** Shown on a question after it was answered. */
  readonly answered: string;
  readonly answerPlaceholder: string;
  readonly sendAnswer: string;
  readonly undo: string;
  readonly undone: string;
  readonly showChanges: string;
  readonly hideChanges: string;
  /** Accessible name of a picture that opens in the lightbox. */
  readonly openImage: string;
}

export interface ChatCopy {
  readonly blocks: BlocksCopy;
  readonly transcript: TranscriptCopy;
  readonly message: MessageCopy;
  readonly tool: ToolCopy;
  readonly run: RunCopy;
  readonly composer: ComposerCopy;
  readonly queue: QueueCopy;
  readonly voice: VoiceCopy;
  readonly room: RoomCopy;
}
