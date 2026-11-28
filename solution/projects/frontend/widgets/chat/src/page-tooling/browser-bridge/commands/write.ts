"use client";

/**
 * Write-style commands — `fill`, `click`.
 *
 * These change the user's data, which is why they were stubs: they needed a
 * confirmation gate designed before the command existed. The gate is
 * `copilot`'s `useProposals`, and it calls `performAction` directly.
 *
 * What is registered here is the SAME executor, reached through the bridge for
 * manual testing (`__chatBridge.fill(...)`). A second implementation would be
 * two answers to "what does a click do", and the one nobody tests would drift.
 * `mutates: true` marks both, and the gate is what branches on it.
 */

import { performAction } from "../perform";
import { registerBridgeCommand } from "../registry";
import { getActiveResolver } from "../set-bridge-resolver";
import type { CSTRefId } from "../overlay/types";

export const fill = registerBridgeCommand({
  name: "fill",
  description: "fill(ref, value) — type into an input (approval required in chat)",
  mutates: true,
  run: (ref: CSTRefId, value: string): Promise<{ outcome: string }> =>
    performAction({ kind: "fill", ref, value }, getActiveResolver()).then((outcome) => ({
      outcome,
    })),
});

/** See `fill`. */
export const click = registerBridgeCommand({
  name: "click",
  description: "click(ref) — click an element (approval required in chat)",
  mutates: true,
  run: (ref: CSTRefId): Promise<{ outcome: string }> =>
    performAction({ kind: "click", ref }, getActiveResolver()).then((outcome) => ({
      outcome,
    })),
});
