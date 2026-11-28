/**
 * Snapshot content hash — staleness detection.
 *
 * A fast non-cryptographic hash (FNV-1a, 32-bit). Two captures of an
 * unchanged page produce the same hash; a changed page produces a
 * different one. Used to decide whether to send a fresh snapshot.
 */

/** FNV-1a 32-bit hash of a string, returned as a hex string. */
export function hashSnapshot(serialized: string): string {
  // FNV-1a constants (32-bit).
  let hash = 0x811c9dc5;
  for (let i = 0; i < serialized.length; i++) {
    hash ^= serialized.charCodeAt(i);
    // hash *= 16777619, kept in 32-bit range via Math.imul.
    hash = Math.imul(hash, 0x01000193);
  }
  // Unsigned, hex.
  return (hash >>> 0).toString(16).padStart(8, '0');
}
