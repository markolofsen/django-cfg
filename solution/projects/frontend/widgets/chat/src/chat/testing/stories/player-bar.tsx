import { useSyncExternalStore } from "react";
import { Button } from "@djangocfg/ui-core/components";

import { SPEEDS, type Fault } from "./scenario";
import type { PlayerSlot } from "./run";

const label = (speed: number): string => (speed === Number.POSITIVE_INFINITY ? "Instant" : `${speed}x`);

const noop = () => () => {};
const none = () => null;

/** Play, pause, step, restart and the speed of the turn in flight, with where it is. */
export function PlayerBar({ slot, onRestart, fault, note }: { readonly slot: PlayerSlot; readonly onRestart: () => void; readonly fault: Fault; readonly note: string }) {
  const player = useSyncExternalStore(slot.subscribe, slot.get, slot.get);
  const state = useSyncExternalStore(player?.subscribe ?? noop, player?.getState ?? none, player?.getState ?? none);
  const live = player !== null && state !== null;
  return (
    <div className="flex flex-col gap-2 border-b border-border p-3 text-sm" role="group" aria-label="Scenario player">
      <div className="flex flex-wrap items-center gap-2">
        {live && state.playing ? (
          <Button size="sm" variant="outline" onClick={() => player.pause()}>Pause</Button>
        ) : (
          <Button size="sm" onClick={() => player?.play()} disabled={!live || state.finished}>Play</Button>
        )}
        <Button size="sm" variant="outline" onClick={() => player?.step()} disabled={!live || state.finished}>Step</Button>
        <Button size="sm" variant="outline" onClick={() => player?.toEnd()} disabled={!live || state.finished}>Jump to end</Button>
        <Button size="sm" variant="outline" onClick={onRestart}>Restart</Button>
        <label className="ms-auto flex items-center gap-2 text-muted-foreground">
          Speed
          <select
            className="h-8 rounded-md border border-input bg-background px-2 text-foreground"
            value={String(live ? state.speed : 1)}
            onChange={(event) => player?.setSpeed(Number(event.target.value))}
            disabled={!live}
          >
            {SPEEDS.map((speed) => (
              <option key={label(speed)} value={String(speed)}>{label(speed)}</option>
            ))}
          </select>
        </label>
      </div>
      <p className="m-0 text-xs text-muted-foreground" aria-live="polite">
        {live ? `Event ${state.index} of ${state.total}${state.finished ? " (end)" : state.playing ? " (playing)" : " (paused)"}` : "Waiting for the turn to start"}
        {fault === "none" ? "" : ` · Fault: ${fault}. ${note}`}
      </p>
    </div>
  );
}
