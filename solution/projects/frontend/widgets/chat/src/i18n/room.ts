import type { RoomCopy } from "./types";

/** Structurally a core `MentionItem`; i18n may not import core. */
export interface RoomMentionItem {
  readonly id: string;
  readonly label: string;
  readonly hint?: string;
  readonly seat?: string;
}

/**
 * The `@` menu items for a room: the assistant first, then the people.
 *
 * Every row is a mention and writes a name, nothing more. The assistant has no `seat` (the server finds it by the text);
 * a person's `seat` is their identity, which rides along as `mentions`.
 */
export function roomMentionItems(
  copy: RoomCopy,
  people: readonly Pick<RoomMentionItem, "id" | "label">[] = [],
): readonly RoomMentionItem[] {
  return [
    { id: "assistant", label: copy.assistant, hint: copy.assistantHint },
    ...people.map(({ id, label }) => ({ id: `person:${id}`, label, seat: id })),
  ];
}
