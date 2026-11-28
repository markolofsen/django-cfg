/**
 * `waiting` — the turn is in flight and has produced nothing yet.
 * `working` — text is arriving; the mark trails the last line.
 *
 * There is deliberately no "done". A resting mark under a finished reply is true
 * of every reply ever sent, so it stacks up one per message and stops carrying
 * information — the mark's whole job is telling the live turn from the settled
 * ones.
 */
export type TurnMarkState = "waiting" | "working";

export interface TurnMarkProps {
  readonly state: TurnMarkState;
  readonly className?: string;
}

/**
 * One shape for the whole life of a turn: waiting, working, done.
 *
 * The states differ only in pace and weight — never in shape — so the end of an
 * answer reads as the mark settling rather than as a new icon appearing. The
 * motion and the sizing are in `styles/turn-mark.css`; this is only the element
 * and its state attribute.
 *
 * `aria-hidden`, always. The transcript's own live region announces a turn's
 * start and end; a mark that also spoke would double every announcement, and it
 * carries no information the region does not already give.
 */
export function TurnMark({ state, className }: TurnMarkProps) {
  return <span className={`turn-mark ${className ?? ""}`} data-state={state} aria-hidden />;
}
