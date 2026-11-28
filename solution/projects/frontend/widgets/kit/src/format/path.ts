/**
 * THE path module for the console — every surface that reads a remote path
 * (document preview, viewers, chat badges, session tree, the New-chat confirm
 * gate) parses it here, so `C:\Users\Марк\file.txt` never renders as its own
 * basename on one pane and correctly on another.
 *
 * **Why one module and not a helper each package re-exports.** The precedent is
 * `ComposerRegistry`, now `@djangocfg/widget-forms/composer-registry`: it lives
 * in its own subpath specifically so
 * neither consumer cross-imports the other, because under Vite's optimizer a
 * cross-tool relative import loads the module TWICE and hands producer and
 * consumer two separate state slots. Five independent path readers are the same
 * defect in a different costume — five slots, five subtly different answers. So
 * callers depend on THIS module directly. Do not re-implement `split("/")`
 * anywhere; do not add a second convention in a feature package.
 *
 * ## Three decisions this module makes deliberately
 *
 * **1. It does not trim.** A trailing space is a legal, real character in a
 * POSIX filename, so trimming inside the parser silently corrupts a path the
 * user actually has. The previous validator (`isAbsolutePathLike`) trimmed and
 * therefore accepted `"  /tmp"` as absolute while sending a different string
 * onward. Trimming is an INPUT-LAYER responsibility: the text field or the
 * dialog decides what the human meant, then hands a settled string here.
 * `unquote` is the one shaping step this module offers, because a quoted path is
 * unambiguously a transport artefact (drag-drop, terminal copy), not content.
 *
 * **2. Backslash is a separator, always — even though POSIX allows it in a
 * filename.** `basename("a\\b")` is genuinely ambiguous and this module answers
 * `"b"`. That is the right default for THIS console: it is a relay whose fleet is
 * majority Windows (14 windows, 9 linux, 7 darwin), and the paths reaching these
 * surfaces are machine-reported paths, not authored filenames. Reading a Windows
 * path wrongly is a guaranteed daily defect; a POSIX file with a literal
 * backslash in its name is a rarity that costs only a shortened label. We trade
 * the rare cosmetic loss for the common correctness win.
 *
 * **3. A dotfile has no extension.** `extension(".gitignore")` is `""` and
 * `basename` is the whole `.gitignore`. The consumers are the viewers, which use
 * the extension to pick a syntax mode or an icon; treating `gitignore` as an
 * extension would make `.gitignore` and `x.gitignore` indistinguishable and would
 * strip the leading dot from the name users recognise. A leading dot names the
 * file; only a LATER dot introduces an extension.
 */

/** Separator run at the end of a path, e.g. the `/` in `/Users/me/`. */
const TRAILING_SEPARATORS = /[\\/]+$/;

/** Matching quote pair a path may arrive wrapped in, from a terminal copy or a
 *  drag-drop payload. Single and double are both seen in the field. */
const QUOTED = /^(["'])([\s\S]*)\1$/;

/** Windows drive root: `C:\` or `D:/`. */
const DRIVE_ROOT = /^[A-Za-z]:[\\/]/;

/** UNC share root: `\\server\share` (or forward-slash spelling). Two leading
 *  separators are what makes it a root; the host name follows. */
const UNC_ROOT = /^[\\/]{2}[^\\/]/;

/**
 * Strips one matching quote pair. A path arriving from a terminal copy or a
 * drag-drop payload is often wrapped because it contains spaces; the quotes are
 * transport, not content. Only ONE pair is removed, and only when both ends
 * match, so a filename that legitimately starts with a quote survives.
 */
export function unquote(path: string | undefined): string {
  const value = path ?? "";
  return QUOTED.exec(value)?.[2] ?? value;
}

/**
 * Canonical form for comparison and for feeding the other functions here:
 * unquoted, with any trailing separator run removed. A root (`/`, `C:\`) keeps
 * its separator, because stripping it would turn a real location into `""` or a
 * bare drive letter.
 *
 * Separators are NOT rewritten to one spelling — the caller may still need to
 * show the path in the host's own convention, and the remote machine owns that.
 */
export function normalize(path: string | undefined): string {
  const value = unquote(path);
  const stripped = value.replace(TRAILING_SEPARATORS, "");
  // Two ways stripping destroys a root rather than tidying a path: `/` and
  // `\\` reduce to `""`, and `C:\` reduces to the bare drive letter `C:`,
  // which names a different thing (the drive's CWD). Keep the original.
  const isBareDrive = /^[A-Za-z]:$/.test(stripped);
  return !stripped || isBareDrive ? value : stripped;
}

/**
 * Last meaningful segment, for compact UI labels. The full path stays with the
 * caller for the tooltip or detail view.
 */
export function basename(path: string | undefined): string {
  const value = normalize(path);
  if (!value) return value;
  const index = Math.max(value.lastIndexOf("/"), value.lastIndexOf("\\"));
  // `|| value` keeps a root readable: slicing `/` past its separator yields
  // `""`, which is a worse label than the root itself.
  return index >= 0 ? value.slice(index + 1) || value : value;
}

/**
 * Lowercased extension WITHOUT the dot, or `""` when the name has none. See
 * decision 3 above for why a leading dot does not count.
 */
export function extension(path: string | undefined): string {
  const name = basename(path);
  const index = name.lastIndexOf(".");
  if (index <= 0) return "";
  return name.slice(index + 1).toLowerCase();
}

/**
 * The path's segments, in order, with separator runs discarded — `["Users",
 * "me", "notes.txt"]`. Both spellings separate, per decision 2.
 *
 * **Why this exists beside `basename`, which is NOT a substitute.** `basename`
 * answers "what do I LABEL this", and returns one string. Tree and navigation
 * callers need the SEGMENTS to rebuild ancestor ids level by level, so before
 * this function they hand-rolled `split(/[/\\]+/)` locally — the exact second
 * convention the header forbids, and how `reveal-path.ts` came to carry its own
 * one-sided UNC test. Segment logic belongs here, once.
 *
 * The ROOT is deliberately not a segment: `/a/b`, `C:\a\b` and `\\nas\a\b` all
 * yield `["a", "b"]` on POSIX, `["C:", "a", "b"]` on a drive path. A caller that
 * needs the root's spelling reads it from the original string, because only the
 * caller knows which separator the host reported.
 */
export function segments(path: string | undefined): string[] {
  const value = normalize(path);
  if (!value) return [];
  return value.split(/[\\/]+/).filter(Boolean);
}

/**
 * The parent directory, or `""` when the path has no parent to name.
 *
 * A root is its own parent (`dirname("/") === "/"`, `dirname("C:\\") === "C:\\"`)
 * rather than `""`: a root is a real location, and reporting "no parent" for it
 * would send a caller looking for one. A bare segment (`"song.mp3"`) genuinely
 * has no parent here, because this module never guesses a base — see the
 * relative-path reasoning in `reveal-path.ts`.
 *
 * The separator is preserved as the caller's own string spelled it, so a
 * Windows path keeps its backslashes and never has to be re-normalised on the
 * way back to the machine that reported it.
 */
export function dirname(path: string | undefined): string {
  const value = normalize(path);
  if (!value) return "";

  const index = Math.max(value.lastIndexOf("/"), value.lastIndexOf("\\"));
  if (index < 0) return "";

  // A separator at position 0 means the parent IS the root; keep the root's own
  // spelling (`/` or the `\` of a `\\unc` path) rather than slicing to `""`.
  if (index === 0) return value.slice(0, 1);
  // `C:\a` → `C:\`, not `C:` — a bare drive letter names the drive's CWD, a
  // different location. Same reasoning as `normalize`'s bare-drive guard.
  if (index === 2 && DRIVE_ROOT.test(value)) return value.slice(0, 3);
  // A UNC root is `\\host\share` — BOTH parts, because `\\host` alone names no
  // location you can list. So the share root is its own parent, exactly as `/`
  // and `C:\` are, and the walk up stops here rather than yielding `\\host`.
  if (UNC_ROOT.test(value) && segments(value).length <= 2) return value;
  return value.slice(0, index);
}

/**
 * Absolute-path SHAPE check — the confirm gate for anything that asks the user
 * to name a remote folder. Accepts a POSIX root, a Windows drive root, and a UNC
 * share; accepts them quoted, since quoting is transport.
 *
 * **`~/` is deliberately NOT absolute.** `~` is a shell convention, not a path:
 * this console cannot know the remote user's home, and the value does not get
 * expanded on the way out — `new-chat-dialog` hands it to `trackProjectRoot`,
 * whose result flows back through `normalizeProjectPath`, which only trims,
 * slash-normalizes and NFC-folds. So a `~/` root would be tracked verbatim and
 * would not match the same folder reached by its real path. Rejecting it at the
 * gate keeps the user's error visible instead of producing a duplicate root.
 *
 * Real validation (exists, is a directory) is the agent's job; this only blocks
 * obviously-relative input client-side.
 *
 * NOTE: no `trim()` — see decision 1. Callers trim their own input.
 */
export function isAbsolute(path: string | undefined): boolean {
  const value = unquote(path);
  return value.startsWith("/") || DRIVE_ROOT.test(value) || UNC_ROOT.test(value);
}

/** Default tail length for {@link elidePath} — enough to name a project. */
const ELIDE_KEEP = 3;

/**
 * A path shortened for DISPLAY, keeping the tail and eliding the head.
 *
 * The tail carries the identity (`…/projects/cmdop_go`); the head is the same
 * boilerplate on every row. This is the head-elision CSS cannot do:
 * `text-overflow` only ever cuts the tail, and flipping `direction` to move the
 * ellipsis inverts the whole line in an RTL locale, which this console
 * supports.
 *
 * DISPLAY only. The full string is what a copy button copies and what a tooltip
 * states — a reader who cannot see the head must still be able to take it.
 *
 * Segment-based rather than character-based, so the result always begins at a
 * real boundary and never cuts a name in half. It reuses {@link segments}, which
 * is also what makes it right on Windows and UNC input; a local `split("/")`
 * would render `C:\Users\me\repo` as one unsplittable blob.
 */
export function elidePath(path: string | undefined, keep = ELIDE_KEEP): string {
  const value = normalize(path);
  if (!value) return "";
  const parts = segments(value);
  if (parts.length <= keep) return value;
  return `…/${parts.slice(-keep).join("/")}`;
}

/** Shortest name worth eliding in the middle — below this the ellipsis costs
 *  more characters than it saves. */
const NAME_ELIDE_MIN = 12;

/**
 * A file NAME shortened in the middle, so the extension always survives.
 *
 * The tail of a filename is the type, and the type is what a reader scans a
 * transcript for. CSS truncation can only ever cut there, which is why a chip
 * labelled `Dikanda - Ederlezi (Nicola Noir …` says nothing about whether it is
 * an mp3, a cue sheet or a folder. Eliding the MIDDLE keeps both ends: the
 * words that identify the file and the suffix that types it.
 *
 * The extension is measured through {@link extension}, so a dotfile keeps its
 * leading dot and is elided as one unbroken name.
 */
export function elideName(name: string, max: number): string {
  if (max < NAME_ELIDE_MIN || name.length <= max) return name;
  const ext = extension(name);
  // The dot belongs to the suffix that is kept whole; a name with no extension
  // simply has none to protect and elides on length alone.
  const suffix = ext === "" ? "" : `.${name.slice(name.length - ext.length)}`;
  // A suffix that eats most of the budget is not a suffix worth protecting —
  // keeping it would leave a head too short to identify anything.
  if (suffix.length > max - NAME_ELIDE_MIN) return `${name.slice(0, max - 1)}…`;
  const head = name.slice(0, max - suffix.length - 1);
  return `${head}…${suffix}`;
}

/**
 * A path for a one-line display: the head elided by SEGMENT, the file name
 * elided in its MIDDLE, so neither end of the identity is lost.
 *
 * {@link elidePath} answers the first half only. It is right where the row can
 * wrap or where the tail is a folder, and wrong on a footer line whose CSS
 * truncates: the head is already gone, and then the browser removes the
 * extension too, leaving a path elided at BOTH ends with no indication that it
 * was. This shortens to a stated budget instead, so what renders is what the
 * function returned.
 *
 * DISPLAY only, exactly as `elidePath` — the full string is what a copy button
 * takes.
 */
export function elidePathLine(path: string | undefined, max: number): string {
  const value = normalize(path);
  if (!value) return "";
  const name = basename(value);
  if (value.length <= max) return value;
  const parts = segments(value);

  // Drop leading segments while the line is still too long, keeping the name
  // and as much of its immediate parentage as fits.
  for (let keep = parts.length - 1; keep >= 2; keep -= 1) {
    const candidate = `…/${parts.slice(-keep).join("/")}`;
    if (candidate.length <= max) return candidate;
  }
  // Only the name is left, and it is what the middle-elide protects.
  return `…/${elideName(name, Math.max(NAME_ELIDE_MIN, max - 2))}`;
}
