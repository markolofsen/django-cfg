import { Volume1, Volume2, VolumeX } from "lucide-react";
import { Button, Popover, PopoverContent, PopoverTrigger, Slider } from "@djangocfg/ui-core";

import { usePlayerCopy } from "../i18n";

/** Below this the speaker glyph loses its second arc — a level, not a mute. */
const QUIET = 0.5;

/** The slider works in percent, so an arrow key moves 1% rather than 0.1%. */
const STEP = 0.01;

export interface VolumeControlProps {
  /** 0…1. The user's intent, not what the element currently reports. */
  readonly volume: number;
  readonly muted: boolean;
  readonly onVolumeChange: (volume: number) => void;
  readonly onToggleMuted: () => void;
  /**
   * False where the platform will not let script set `volume` — iOS, where it
   * is read-only. The slider is then ABSENT rather than disabled: a control
   * that cannot work is worse than one that is not offered.
   *
   * A FACT measured by whoever mounts this, never sniffed from a user agent
   * here. Two owners of "can we change the volume" would disagree the day a
   * browser changes.
   */
  readonly canChangeVolume?: boolean;
}

/**
 * Volume: an icon that opens a slider, not a slider on the row.
 *
 * It is the least-used of the row's controls and would cost the title its width
 * at every viewport. Behind a button it costs one press only when wanted, which
 * is the trade every desktop player makes for the same reason.
 *
 * The dock argued for years that the OS owns volume. That is true of a phone and
 * false of a browser: OS volume is not per-tab, so lowering a recording means
 * lowering the call you are on. Chrome's tab mute is the only per-tab control
 * and it is all-or-nothing.
 *
 * The popover holds a slider, never the media element — an unmounted subtree
 * would take the element with it and restart the track.
 */
export function VolumeControl({
  volume,
  muted,
  onVolumeChange,
  onToggleMuted,
  canChangeVolume = true,
}: VolumeControlProps) {
  const copy = usePlayerCopy();

  const silent = muted || volume === 0;
  const label = silent ? copy.controls.unmute : copy.controls.mute;

  // data-before-jsx (`@rules`, gated by check-jsx-boundary).
  const icon = silent
    ? <VolumeX aria-hidden className="size-4" />
    : volume < QUIET
      ? <Volume1 aria-hidden className="size-4" />
      : <Volume2 aria-hidden className="size-4" />;

  const toggle = (
    <Button
      variant="ghost"
      size="icon"
      elevated={false}
      onClick={onToggleMuted}
      aria-label={label}
      tooltip={label}
      className="size-8 shrink-0 rounded-full text-muted-foreground"
    >
      {icon}
    </Button>
  );

  // No slider where the platform will not honour one. The BUTTON stays: mute is
  // the half that works everywhere, and it is the half a reader reaches for.
  if (!canChangeVolume) return toggle;

  const onSliderChange = (next: number[]) => {
    const level = next[0];
    if (level === undefined) return;
    onVolumeChange(level);
  };

  return (
    <Popover>
      {/* The trigger WRAPS the button rather than replacing it: pressing the
          glyph must still mute, which is the fast path, while the slider is one
          hover away. Radix opens on pointerdown, so the click that mutes and the
          gesture that opens are the same press. */}
      <PopoverTrigger asChild>{toggle}</PopoverTrigger>
      <PopoverContent side="top" align="center" className="w-auto p-3">
        <Slider
          value={[muted ? 0 : volume]}
          min={0}
          max={1}
          step={STEP}
          orientation="vertical"
          onValueChange={onSliderChange}
          aria-label={copy.controls.volume}
          className="h-24"
        />
      </PopoverContent>
    </Popover>
  );
}
