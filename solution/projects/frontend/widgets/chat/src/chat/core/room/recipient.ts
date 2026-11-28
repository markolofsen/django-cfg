/**
 * Who a line is for, and the `@` mentions in its text.
 *
 * A call chat has two kinds of line: one for everyone in the room (the default) and a private one to a single person.
 * The assistant is NEVER a recipient: a question to it is a plain line, and `@assistant` is a mention like any other that
 * the server answers by itself. So a recipient is chosen with a control (the chip above the field), never by typing; the `@`
 * menu only writes names into the text, and the seats named there ride along as `mentions` for highlights and badges.
 *
 * Pure and DOM-free, like the rest of `core/`.
 */

/** One seat that can be written to or mentioned. `id` is the seat identity the server knows. */
export interface Person {
  readonly id: string;
  readonly label: string;
}

/** `"all"`: every seat reads it. A person: a private line that only that seat and the sender read. */
export type Recipient = "all" | Person;

/** What a line with no chosen recipient is for. */
export const defaultRecipient: Recipient = "all";

/** The room, or one other seat. */
export const isPrivate = (recipient: Recipient): recipient is Person => recipient !== "all";

/** The id the wire takes as `recipient_id`: the seat for a private line, nothing for the room. */
export const recipientId = (recipient: Recipient): string | undefined =>
  isPrivate(recipient) ? recipient.id : undefined;

/** The most seats a line can mention (the server drops the rest). */
export const MAX_MENTIONS = 8;

/**
 * The people a recipient can be picked from: the roster without this seat and without the assistant, in the roster's order.
 * Which of them are in the call now is not decided here (a seat that left can still be written to).
 */
export function pickablePeople(roster: readonly Person[], selfId: string, assistantId = "assistant"): readonly Person[] {
  return roster.filter((person) => person.id !== selfId && person.id !== assistantId);
}

/** Keep a sticky recipient only while the roster still lists it; a stale one falls back to the room. */
export function stillPickable(recipient: Recipient, roster: readonly Person[]): Recipient {
  return isPrivate(recipient) && !roster.some((person) => person.id === recipient.id) ? defaultRecipient : recipient;
}

/**
 * One row of the `@` menu, supplied by the host. Choosing a row only writes `@label` into the text.
 * `seat` is the seat identity the mention names; absent for the assistant, whom the server finds by the text itself.
 */
export interface MentionItem {
  readonly id: string;
  /** The text written after `@`. May contain spaces ("Mark Olofsen"). */
  readonly label: string;
  /** A line beside the label in the menu. */
  readonly hint?: string;
  readonly seat?: string;
}

/** The token as written into the message. */
export function mentionToken(item: MentionItem): string {
  return `@${item.label}`;
}

/**
 * The items a query selects, in the host's order.
 *
 * A prefix match on the label, case-insensitive. A prefix and not a substring:
 * the menu opens on a bare `@`, and the list must narrow toward what the sender
 * is spelling, not rearrange itself around a letter in the middle of a name.
 */
export function filterMentionItems(items: readonly MentionItem[], query: string): readonly MentionItem[] {
  const wanted = query.toLocaleLowerCase();
  return items.filter((item) => item.label.toLocaleLowerCase().startsWith(wanted));
}

const escape = (text: string): string => text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** A mention found in a text: where it starts, how long the token is, and the item it names. */
export interface MentionSpan {
  readonly start: number;
  readonly end: number;
  readonly item: MentionItem;
}

/**
 * Every mention in the text, left to right, never overlapping.
 *
 * The longest label at a position wins, so "@Assistant Bot" is one mention and not "@Assistant" followed by a word.
 * A token must start the text or follow whitespace and must not run into a letter or digit, so an e-mail address and
 * "@Assistants" mention no one.
 */
export function mentionSpans(text: string, items: readonly MentionItem[]): readonly MentionSpan[] {
  const found: MentionSpan[] = [];
  for (const item of items) {
    const pattern = new RegExp(`(?<=^|\\s)${escape(mentionToken(item))}(?![\\p{L}\\p{N}_])`, "giu");
    for (const match of text.matchAll(pattern)) {
      found.push({ start: match.index, end: match.index + match[0].length, item });
    }
  }
  found.sort((a, b) => a.start - b.start || b.end - a.end);
  const spans: MentionSpan[] = [];
  let coveredUntil = -1;
  for (const span of found) {
    if (span.start < coveredUntil) continue;
    coveredUntil = span.end;
    spans.push(span);
  }
  return spans;
}

/** The seats a text names, in order of first mention, each once, at most {@link MAX_MENTIONS}. */
export function mentionedSeats(text: string, items: readonly MentionItem[]): readonly string[] {
  const seats: string[] = [];
  for (const { item } of mentionSpans(text, items)) {
    if (item.seat !== undefined && !seats.includes(item.seat)) seats.push(item.seat);
  }
  return seats.slice(0, MAX_MENTIONS);
}

/** Whether the text names the assistant (the mention item without a seat). */
export function mentionsAssistant(text: string, items: readonly MentionItem[]): boolean {
  return mentionSpans(text, items).some(({ item }) => item.seat === undefined);
}
