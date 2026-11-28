import { CFG_FAMILIES, cfgStorage } from "@djangocfg/api/storage";
/**
 * What a persisted draft is worth keeping, as a pure decision.
 *
 * The effects that read and write live in `composer/use-draft-persistence.ts`;
 * the RULES live here so they can be tested without a DOM. This workspace has
 * no jsdom, so a rule that stays inside a hook is a rule nothing can assert.
 */

/** A draft larger than this is a paste, not typing, and belongs in a chip. */
export const DRAFT_MAX_LENGTH = 100_000;


/**
 * The storage key for a room. Spelled like `useSpeechLanguage` (ui-core `lib/speech-language`), so
 * chat's keys share one convention.
 *
 * Unversioned: the value is a plain string, so the only migration a version
 * could gate is "it became structured" — and that wants a new prefix, leaving
 * the old entries to expire with their session.
 */
export function draftStorageKey(room: string): string {
  return cfgStorage.familyKey(CFG_FAMILIES.chatDraft, room);
}

/**
 * What to do with a value read back from storage.
 *
 * `null` for both "nothing stored" and "stored empty": an empty string would
 * otherwise CLEAR a field the host had already seeded, which is the one
 * outcome a restore must never produce. Over-long values are truncated rather
 * than dropped — losing the tail of a long draft beats losing all of it.
 */
export function restoredDraft(stored: string | null): string | null {
  if (stored === null || stored === "") return null;
  return stored.length > DRAFT_MAX_LENGTH ? stored.slice(0, DRAFT_MAX_LENGTH) : stored;
}

/**
 * Whether writing this text means storing it or removing the entry.
 *
 * Empty means REMOVE, which is what makes a send clear the draft with no
 * send-specific branch: `send` resets the draft, the save path sees `""`, and
 * the entry goes. Keeping an empty string instead would leave every sent room
 * holding a useless entry forever.
 */
export function draftWrite(text: string): { readonly remove: true } | { readonly value: string } {
  if (text === "") return { remove: true };
  return { value: text.slice(0, DRAFT_MAX_LENGTH) };
}

/**
 * Whether the save path may write yet.
 *
 * Before a room's restore has run, the draft still holds the PREVIOUS room's
 * text (or the empty initial value). Writing then puts one room's draft under
 * another's key, or erases a stored draft with the emptiness that precedes its
 * own restore — the second is silent and destroys real work.
 */
export function mayPersist(restoredRoom: string | null, room: string): boolean {
  return restoredRoom === room;
}
