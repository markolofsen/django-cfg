import { Suspense, lazy } from "react";
import { FileText } from "lucide-react";

/**
 * The typed icon set, behind a hard `React.lazy` boundary.
 *
 * Measured at 476 KB as its own chunk, so it must never reach the boot path,
 * and a dynamic import is a boundary the bundler cannot collapse.
 *
 * The player's dock made this non-negotiable rather than merely prudent: it
 * renders on every screen, so a static import here would put the whole set in
 * front of the host's first paint.
 */
const LazyFileIcon = lazy(async () => {
  const mod = await import("@djangocfg/widget-data/file-icon");
  return { default: mod.FileIcon };
});

/**
 * The sizes the icon set actually ships.
 *
 * A closed union, not a number: the artwork is drawn per size rather than
 * scaled, so an arbitrary value has nothing to render. Re-exported so a caller
 * picking a size is told at compile time rather than shipping a blank box.
 */
export type FileGlyphSize = 12 | 14 | 16 | 18 | 20 | 24 | 28 | 32 | 40 | 48 | 64;

export interface FileGlyphProps {
  /**
   * The path or bare filename to type the icon from.
   *
   * A PATH is accepted because most callers have one; the basename is taken
   * here so no caller has to know that the lookup keys on it.
   */
  readonly path: string;
  /** Pixel edge. The surface decides; there is no default worth defaulting to. */
  readonly size?: FileGlyphSize;
  readonly className?: string;
}

/**
 * The ONE typed file icon.
 *
 * Every surface that answers "what kind of file is this" draws it through here:
 * the chat's reference card and chip, and the player's artwork fallback. Before
 * this each had its own answer, and the same `.mp3` appeared as a red disc in a
 * chip and a grey Lucide note in the player two rows below it.
 *
 * **It types the FILE, it does not stand in for artwork.** A track with an
 * embedded cover shows the cover; this is what a file with none falls back to.
 * The two are different questions and only one of them has a single answer.
 *
 * The fallback is a generic document rather than a gap, so the swap is a glyph
 * gaining detail — never a hole opening mid-sentence while a chunk loads.
 */
export function FileGlyph({ path, size, className }: FileGlyphProps) {
  const folder = isFolderPath(path);
  return (
    <Suspense fallback={<FileText aria-hidden className={className} />}>
      <LazyFileIcon name={fileGlyphName(path)} isFolder={folder} size={size} className={className} />
    </Suspense>
  );
}

/**
 * The basename the icon lookup keys on.
 *
 * Both separators: a revealable path may be a Windows one (`C:\src\main.go`),
 * and splitting on `/` alone would hand the table the whole string and match
 * nothing.
 *
 * Returns the input unchanged when there is no segment to take, so a caller
 * always has a string to look up — the table answers a generic icon for
 * anything it does not know.
 */
export function fileGlyphName(path: string): string {
  const trimmed = path.replace(/[/\\]+$/, "");
  if (trimmed === "") return path;
  const cut = Math.max(trimmed.lastIndexOf("/"), trimmed.lastIndexOf("\\"));
  return cut === -1 ? trimmed : trimmed.slice(cut + 1) || trimmed;
}

/**
 * Whether to draw a folder rather than a typed file icon.
 *
 * A trailing separator is the ONLY signal available here, and it is a weak one:
 * an agent naming a directory without it gets a file glyph. That is deliberate
 * — the alternative is asking the machine what a path is before drawing a chip,
 * which is a round-trip per reference for a glyph. A hover card answers
 * authoritatively; this only has to be right often enough to help.
 */
export function isFolderPath(path: string): boolean {
  return /[/\\]$/.test(path.trim());
}
