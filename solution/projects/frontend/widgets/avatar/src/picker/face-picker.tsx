import { RotateCcw, Shuffle } from "lucide-react";
import { Button } from "@djangocfg/ui-core";

import { type AvatarKind } from "../registry/corpora";
import { SeededAvatar } from "../render/seeded-avatar";

export interface FacePickerProps {
  /** The seed drawn right now — chosen or derived, the picker cannot tell. */
  readonly seed: string;
  /**
   * WHICH corpus the seed is drawn from — the same axis `SeededAvatar` takes.
   *
   * Without it the picker drew every subject as a person, so a ROOM previewed a
   * face here and rendered its silhouette everywhere else: the operator chose
   * one thing and the roster showed another. The roster already states the rule
   * this restores — a room given a face would claim to be a person, and the
   * silhouette is what separates the two before any glyph is read.
   *
   * Defaults to `person`, which is what every existing caller was already
   * getting, so adding this changes no face that was correct.
   */
  readonly kind?: AvatarKind;
  /** Whether `seed` is a CHOICE rather than the derived default. Drives the
   *  reset affordance, which must not offer to undo something nobody did. */
  readonly chosen: boolean;
  /** Report a new choice. An empty string clears back to the derived face. */
  readonly onChange: (seed: string) => void;
  /** Rendered size in px. The face is the subject here, so callers give it room. */
  readonly size?: number;
  readonly shuffleLabel: string;
  readonly resetLabel: string;
  readonly disabled?: boolean;
}

/**
 * Pick a face by SHUFFLING, not by assembling one.
 *
 * The owner's call, and it is what keeps a stored choice safe: a seed survives
 * any theme that still hashes it, while a config naming `eyes: "dots"` is a
 * hostage to the option list — upgrade the theme, lose the option, and someone's
 * face renders as something else.
 *
 * It is also the honest shape for the job. Choosing a face is recognising one,
 * not specifying it; per-feature tabs would ask an operator to describe what
 * they will know on sight.
 *
 * The controls sit ON the face rather than beside it. Three items in a row read
 * as three peers — the first version put a 40px face between two buttons and it
 * looked like the smallest of them, while the roles listed below wore larger
 * ones. The subject should be the biggest thing here, and its verbs attach to
 * it.
 */
export function FacePicker({
  seed,
  kind,
  chosen,
  onChange,
  size = 96,
  shuffleLabel,
  resetLabel,
  disabled,
}: FacePickerProps) {
  // A fresh random seed. The alphabet is irrelevant to the drawing — the style
  // hashes whatever it is given — so this only has to be unlikely to repeat.
  //
  // One seed now moves BOTH the drawing and the art style it is drawn in, so a
  // shuffle can cross from a line drawing to a robot. That is the point: a
  // shuffle confined to one style could only ever offer variations of one look.
  const shuffle = () => onChange(Math.random().toString(36).slice(2, 10));

  // Reset appears only once a choice exists: clearing is a real act with a real
  // effect, and offering it against the derived face would be a control that
  // does nothing.
  let resetNode = null;
  if (chosen) {
    resetNode = (
      <Button
        type="button"
        variant="secondary"
        aria-label={resetLabel}
        title={resetLabel}
        disabled={disabled}
        onClick={() => onChange("")}
        className="absolute -bottom-1 -left-1 h-8 w-8 rounded-full p-0 shadow-sm"
      >
        <RotateCcw className="h-3.5 w-3.5" aria-hidden />
      </Button>
    );
  }

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <span className="block overflow-hidden rounded-full" style={{ width: size, height: size }}>
        <SeededAvatar seed={seed} kind={kind} size={size} />
      </span>
      {/* Icon-only, because the face beside it already says what it changes. A
          worded button would be wider than the subject it acts on. */}
      <Button
        type="button"
        variant="secondary"
        aria-label={shuffleLabel}
        title={shuffleLabel}
        disabled={disabled}
        onClick={shuffle}
        className="absolute -bottom-1 -right-1 h-8 w-8 rounded-full p-0 shadow-sm"
      >
        <Shuffle className="h-3.5 w-3.5" aria-hidden />
      </Button>
      {resetNode}
    </div>
  );
}
