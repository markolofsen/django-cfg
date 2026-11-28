/**
 * The face a ROLE wears, wherever it is offered.
 *
 * Seeded by the SLUG, so one persona is the same character in every surface
 * that names it — a catalogue listing, a detail page, a create dialog. That
 * consistency is the whole point: someone who recognises a face in a catalogue
 * and installs it must meet that face in the product.
 *
 * It deliberately differs from the face an INSTALLED instance wears, which a
 * host seeds by that instance's own address — two instances of one role are two
 * correspondents and must be told apart. The listing answers "which persona";
 * the roster row answers "which instance".
 */
export function roleAvatarSeed(slug: string): string | undefined {
  // An empty slug is not a persona and has no face. An empty seed would still
  // draw one, giving a default a character it does not have.
  return slug || undefined;
}
