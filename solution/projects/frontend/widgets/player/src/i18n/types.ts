/**
 * The player package's copy schema.
 *
 * English is the schema of record: every locale dictionary is typed against
 * `PlayerCopy`, so a missing or misspelled key fails `tsc` rather than rendering
 * `undefined` into a transport button.
 *
 * Typing is what REPLACES the shared locale gates here. The four scripts under
 * `packages/i18n/scripts/` walk the catalogue in `packages/i18n/src/locales/`
 * and cannot see a package-local dictionary, exactly as they cannot see the chat
 * or onboarding ones.
 */

/**
 * What went wrong, as sentences that name a CAUSE.
 *
 * Every member is specific and there is deliberately no generic "something went
 * wrong" for a known reason: unattributed silence is the failure this package
 * exists to remove, and a vague message reproduces it with extra steps.
 */
export interface FailureCopy {
  /** `{{machine}}` is the machine that went away. */
  readonly machineUnreachable: string;
  /** The same fact when the track carries no machine name. */
  readonly machineUnreachableUnnamed: string;
  readonly refused: string;
  readonly unknown: string;
  /**
   * The autoplay refusal, and the ONE string here that is not an apology.
   *
   * It is the only member that is not a fault — the file is fine and one click
   * fixes it — so it must read as an instruction. Every other string ends
   * "playback stopped"; this one says "press play".
   */
  readonly blocked: string;
}

/** The transport every surface shares: the same three verbs, one vocabulary. */
export interface TransportCopy {
  readonly play: string;
  readonly pause: string;
  /**
   * The same two acts, as the ARTWORK announces them.
   *
   * Distinct strings because the row renders two controls for one act, and two
   * buttons a screen reader reads identically are two buttons it cannot tell
   * apart. These name the target as well as the verb.
   */
  readonly playFromCover: string;
  readonly pauseFromCover: string;
  /** Ends the track AND removes the surface. Both halves, because both happen. */
  readonly dismiss: string;
  /** Terminal receipt: the file reached its end on its own. */
  readonly ended: string;
}

/**
 * Copy for the footer dock — the small surface a track lives in by default.
 *
 * `label` names the region so the landmark is not anonymous, and `expand` names
 * the control that opens the stage. The dock is a REMOTE CONTROL with a picture
 * attached, not a place to watch something.
 */
export interface DockCopy {
  readonly label: string;
  /** Opens the stage. Names the destination, not the gesture. */
  readonly expand: string;
  /** Reveals the file in its machine's tree. */
  readonly openInFiles: string;
  /**
   * Opens the panel — the detail beside the row, for a track with no stage.
   *
   * Distinct from {@link expand}, which goes to the stage: audio has nothing to
   * watch, so its detail belongs in the footer rather than on a route.
   */
  readonly showDetails: string;
  /** Closes it again. A separate string because the label states the next act. */
  readonly hideDetails: string;
}

/**
 * Copy for the stage — the route where a video is actually watched.
 *
 * Short, because the stage owns little: the dock's row stays on screen beneath
 * it and carries the transport, the title and the way back. There is no `back`
 * string here for that reason — the control that leaves belongs to the dock.
 */
export interface StageCopy {
  /** Names the region, so the route is not anonymous to a screen reader. */
  readonly label: string;
  /** The stage with nothing loaded — a stale deep link, not an error. */
  readonly empty: string;
  /** Returns the picture to the footer without stopping it. Lives on the dock. */
  readonly minimize: string;
}

/**
 * Copy for the controls that MOVE something — the scrubber and the volume.
 *
 * Separate from {@link TransportCopy} because those are the three verbs every
 * surface shares; these belong to controls only a surface with room renders.
 */
export interface ControlsCopy {
  /** Names the scrubber. The label a screen reader reads before the time. */
  readonly seek: string;
  /** Names the volume control. */
  readonly volume: string;
  /** Silences it. */
  readonly mute: string;
  /** Restores the sound. A separate string: the label states the next act. */
  readonly unmute: string;
}

/**
 * Copy for the metadata popover — the field LABELS, not the values.
 *
 * Every value here comes from the file itself and is never translated: a codec
 * is `aac` in every language, and a path is a path. What needs a locale is the
 * word in front of it.
 */
export interface InfoCopy {
  /** Names the control that opens the popover, and the popover's own region. */
  readonly label: string;
  readonly artist: string;
  readonly album: string;
  /** Which machine the file is on. Always a NAME, never an id. */
  readonly machine: string;
  /** Shown in place of a machine name the roster no longer knows. */
  readonly machineUnknown: string;
  /** Takes the FULL path, which the elided line on screen does not carry. */
  readonly copyPath: string;
  /** Reveals the file among its siblings — a different act from playing it. */
  readonly revealFolder: string;
  /** Takes a LINK that reopens this track for someone else, not the path. */
  readonly share: string;
}

export interface PlayerCopy {
  readonly transport: TransportCopy;
  readonly controls: ControlsCopy;
  readonly info: InfoCopy;
  readonly dock: DockCopy;
  readonly stage: StageCopy;
  readonly failure: FailureCopy;
}
