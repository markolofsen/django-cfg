import type { MediaFailure } from "../domain";

import { fill, type FailureCopy } from "../i18n";

/**
 * Render a failure as a sentence that names its CAUSE.
 *
 * Every branch is specific, and there is deliberately no generic
 * "something went wrong" for a KNOWN reason: unattributed silence is the failure
 * this package exists to remove, and a vague message reproduces it with extra
 * steps. `unknown` is the one case where the browser genuinely told us nothing.
 *
 * One function, not a switch per surface. The dock and the stage previously
 * carried the same switch each, which is two places for a new failure member to
 * be forgotten in — and forgetting one renders the default, so it looks handled.
 */
export function failureText(failure: MediaFailure, copy: FailureCopy): string {
  switch (failure.reason) {
    case "machine-unreachable":
      return failure.machineId
        ? fill(copy.machineUnreachable, { machine: failure.machineId })
        : copy.machineUnreachableUnnamed;
    case "refused":
      return copy.refused;
    case "blocked":
      // Not a fault: the browser wants a gesture and the file is fine. It asks
      // for a click rather than reporting that something stopped.
      return copy.blocked;
    case "unknown":
      return copy.unknown;
  }
}
