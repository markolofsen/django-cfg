import { useState } from "react";
import { Music, Video } from "lucide-react";
import { FileGlyph, type FileGlyphSize } from "../ui";
import type { MediaKind } from "../domain";

export interface TrackCoverProps {
  /** Artwork URL. Absent for most files, which is why the tile exists. */
  readonly src?: string;
  readonly kind: MediaKind;
  /** Edge length in pixels. Square, always. */
  readonly size: number;
  /**
   * The file's path, used to TYPE the fallback glyph.
   *
   * Absent for a track that is not a machine file — a URL or a data source has
   * no extension to look up — in which case the tile names the medium instead.
   */
  readonly path?: string;
}

/**
 * The icon set ships fixed sizes, so the tile's edge is mapped to the nearest
 * one at or below 45% of it — the proportion the medium glyph already used.
 * Rounding DOWN keeps the mark inset: an icon drawn edge-to-edge in its own
 * plate reads as cropped.
 */
const GLYPH_SIZES: readonly FileGlyphSize[] = [12, 14, 16, 18, 20, 24, 28, 32, 40, 48, 64];

function glyphSize(edge: number): FileGlyphSize {
  const target = edge * 0.45;
  let chosen: FileGlyphSize = GLYPH_SIZES[0] as FileGlyphSize;
  for (const candidate of GLYPH_SIZES) {
    if (candidate <= target) chosen = candidate;
  }
  return chosen;
}

/** What a track with no path falls back to: the medium, not a file type. */
function MediumGlyph({ kind, size }: { readonly kind: MediaKind; readonly size: number }) {
  const Icon = kind === "video" ? Video : Music;
  return (
    <Icon
      aria-hidden
      strokeWidth={1.5}
      className="text-muted-foreground"
      style={{ width: size * 0.45, height: size * 0.45 }}
    />
  );
}

/**
 * A track's artwork, or a placeholder tile of the same size.
 *
 * The placeholder is the DEFAULT VIEW, not an error state: most files carry no
 * embedded artwork at all. That is why it is a tile rather than a bare icon — an
 * empty square of the right size keeps every row the same shape whether or not a
 * file happens to have art.
 *
 * **The `onError` fallback is the load-bearing part.** A cover URL points at the
 * relay's cover route, which can 404 for a file whose art was stripped, or fail
 * outright when the machine goes away mid-transcript. Without it the row shows a
 * broken-image glyph — an error where the honest answer is "this file has no
 * picture".
 *
 * Owned here rather than taken from the retired `@djangocfg/ui-tools/audio-player`: that
 * import would pull a whole player kit into this package for one 40px tile, and
 * the kit's player is exactly what this package replaces.
 */
export function TrackCover({ src, kind, size, path }: TrackCoverProps) {
  const [errored, setErrored] = useState(false);

  const style = { width: size, height: size };

  if (!src || errored) {
    // The console's ONE typed file glyph, not a medium-generic note.
    //
    // This tile and the chat's reference card show the same files, often two
    // rows apart, and they used to disagree: a chip drew the branded `.mp3`
    // mark while the player drew a grey Lucide note. Same file, same question,
    // two answers.
    //
    // It falls back to naming the MEDIUM when there is no path to type from —
    // a track built from a URL rather than a machine file.
    return (
      <span
        className="grid shrink-0 place-items-center rounded-md bg-muted"
        style={style}
        data-testid="track-cover-placeholder"
      >
        {path === undefined
          ? <MediumGlyph kind={kind} size={size} />
          : <FileGlyph path={path} size={glyphSize(size)} />}
      </span>
    );
  }

  return (
    <img
      src={src}
      alt=""
      width={size}
      height={size}
      loading="lazy"
      decoding="async"
      onError={() => setErrored(true)}
      className="block shrink-0 rounded-md object-cover"
      style={style}
    />
  );
}
