import { useTurn } from "../../store";

/**
 * `waiting` — sent, nothing back yet. `working` — text is arriving.
 * `null` — no turn in flight, so nothing to mark.
 */
export type TurnActivity = "waiting" | "working" | null;

/**
 * The live turn's activity, in one place.
 *
 * Derived from `useTurn`, never stored: the two flags it reads are themselves
 * derived from the transcript, and a third copy could disagree with both about
 * whether an answer has started.
 *
 * It exists so the trailing indicator has ONE owner. The alternative — each
 * message row deciding from its own `status` — puts the answer in as many places
 * as there are messages, and every settled row then answers "yes, I finished",
 * which is how a marker ends up stacked once per reply on a single screen.
 */
export function useTurnActivity(): TurnActivity {
  const { isStreaming, isPending } = useTurn();
  if (!isStreaming) return null;
  return isPending ? "waiting" : "working";
}
