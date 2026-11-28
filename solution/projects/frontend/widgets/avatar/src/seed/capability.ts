/**
 * The mark a CAPABILITY wears — a skill, or a tool server.
 *
 * Seeded by the SLUG, for the same reason `roleAvatarSeed` is: it is an
 * address, it survives a rename, and it is identical on both sides of the wire
 * — so an entry recognised in a catalogue is the entry met after installing.
 *
 * Two functions rather than one shared `capabilityAvatarSeed`, though today
 * their bodies are the same line. They are two product decisions that merely
 * agree right now: if tool servers ever seed by a canonical name — they may
 * have one, and skills do not — that is a one-line change here instead of a new
 * branch at every call site. The cost of the duplication is two lines; the cost
 * of the shortcut is a caller passing the wrong string.
 */

/**
 * A published skill has a slug by construction, so the empty answer is a
 * defensive one — but it is the same contract `roleAvatarSeed` states, and a
 * caller must never have to ask which of the three behaves differently.
 */
export function skillAvatarSeed(slug: string): string | undefined {
  return slug || undefined;
}

export function mcpAvatarSeed(slug: string): string | undefined {
  return slug || undefined;
}
