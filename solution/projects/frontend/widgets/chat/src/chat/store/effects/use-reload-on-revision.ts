import { useEffect, useRef } from "react";

import { reloadDecision } from "../../core/room/reload-decision";
import { useTurn } from "../hooks";

/**
 * Re-read the room when something outside this tab changed it.
 *
 * The caller supplies a REVISION — a number that moves when the room moved —
 * and a `reload` that re-fetches history. `reloadDecision` owns the rule; this
 * owns the refs, because the decision needs values a render cannot hold: what
 * revision was last acted on, and whether a change is owed.
 *
 * A number rather than the events themselves, because the package must not
 * depend on the host's bus or its stores. What "the room moved" MEANS is the
 * host's to decide — a server hint, a reconnect, a manual refresh — and all this
 * needs is that the number changed.
 *
 * `room` is optional and identifies WHICH room the revision counts for. A host
 * that mounts this hook once per room can omit it; one that keeps a single
 * mount across rooms must pass it, or two rooms' counters are compared as if
 * they were one room's.
 */
export function useReloadOnRevision(
  revision: number,
  reload: () => void,
  room?: string,
): void {
  const { isStreaming } = useTurn();
  // Seeded with the opening revision: a room has just read its history, so the
  // first value is not a change.
  const seen = useRef(revision);
  const deferred = useRef(false);
  // Which room `seen` describes. Revisions are per-room counters, so comparing
  // one room's against another's is meaningless — and not merely noise: a room
  // left at 3 followed by a fresh room reading 0 counts as a change and fires a
  // reload over the history that room just fetched. That used to be impossible
  // because the host remounted this hook per room; it is possible now, so the
  // re-seed has to be explicit.
  const seenRoom = useRef(room);
  if (seenRoom.current !== room) {
    seenRoom.current = room;
    seen.current = revision;
    deferred.current = false;
  }
  // Read through a ref so a caller may pass an inline arrow without re-arming
  // the effect on every render.
  const reloadRef = useRef(reload);
  reloadRef.current = reload;

  useEffect(() => {
    const decision = reloadDecision({
      revision,
      seen: seen.current,
      streaming: isStreaming,
      deferred: deferred.current,
    });
    seen.current = revision;
    if (decision === "ignore") return;
    if (decision === "defer") {
      deferred.current = true;
      return;
    }
    deferred.current = false;
    reloadRef.current();
  }, [revision, isStreaming]);
}
