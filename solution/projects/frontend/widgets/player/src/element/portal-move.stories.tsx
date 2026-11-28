import { useState } from "react";
import { createPortal } from "react-dom";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, userEvent, waitFor, within } from "storybook/test";

import { MediaElement } from "./media-element";
import { silentWavDataUrl } from "./media-fixture";

/**
 * Why this package does NOT portal one element between surfaces.
 *
 * The original design was that a single media element serves the dock, the
 * route and a transcript card by being portalled between them, so a video could
 * survive navigation without a second element ever existing. This story was
 * written to prove that property before anything was built on it.
 *
 * **It disproved it.** Changing a portal's `container` does not re-parent the
 * node: React unmounts the tree from the old container and mounts a NEW one in
 * the new container. The original element ends up detached — `parentElement`
 * is null — and the element that appears in the destination is a different DOM
 * node that merely serializes identically. A media element recreated that way
 * reloads its source and restarts at zero.
 *
 * The story is kept, inverted, because the claim is not obvious: portals are
 * routinely described as "rendering into another part of the DOM", which reads
 * like a move. The surfaces therefore share ONE mounted element by position, not
 * by portal — see the plan for the shape that replaced this.
 *
 * Delete this story only when React documents the opposite behaviour, and
 * replace it with one that proves the new behaviour rather than removing the
 * evidence.
 */

const SRC = silentWavDataUrl();

/** Where the element can live. The names are the surfaces they stand in for. */
type Slot = "dock" | "stage";

function PortalHarness() {
  const [slot, setSlot] = useState<Slot>("dock");
  // Containers are held in STATE, not refs. A ref assignment does not re-render,
  // so a portal target read from `ref.current` during render stays pinned to
  // whichever container existed first, and the element never moves at all.
  const [dock, setDock] = useState<HTMLDivElement | null>(null);
  const [stage, setStage] = useState<HTMLDivElement | null>(null);
  const target = slot === "dock" ? dock : stage;

  return (
    <div>
      <button
        type="button"
        onClick={() => {
          const el = document.querySelector<HTMLMediaElement>("[data-testid='element']");
          if (el === null) return;
          void el.play().catch((cause: unknown) => {
            // Report a refusal on the element rather than as an unhandled
            // rejection, so a failure names its cause instead of timing out.
            el.dataset.playError = cause instanceof Error ? cause.name : String(cause);
          });
        }}
      >
        Start
      </button>
      <button type="button" onClick={() => setSlot(slot === "dock" ? "stage" : "dock")}>
        Move
      </button>
      <div data-testid="dock" ref={setDock} />
      <div data-testid="stage" ref={setStage} />
      {target !== null
        ? createPortal(
            <MediaElement kind="audio" src={SRC} data-testid="element" preload="auto" />,
            target,
          )
        : null}
    </div>
  );
}

const meta = {
  title: "Widgets/Player/Element / Portal move",
  component: PortalHarness,
  parameters: { layout: "padded" },
} satisfies Meta<typeof PortalHarness>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Moving a portal RECREATES the element; it does not re-parent it.
 *
 * Playback is started by clicking, and the suite runs Chromium with
 * `--autoplay-policy=no-user-gesture-required` — a synthesized click does not
 * satisfy the real-gesture requirement, so without that flag no media story
 * could ever start playback.
 */
export const MovingAPortalRecreatesTheElement: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const dock = canvas.getByTestId("dock");
    const element = (await canvas.findByTestId("element")) as HTMLMediaElement;

    await expect(dock.contains(element)).toBe(true);

    await userEvent.click(canvas.getByRole("button", { name: "Start" }));
    // A refusal is reported as a named error rather than an unhandled
    // rejection, so a failure here says WHY instead of timing out on the clock.
    await expect(element.dataset.playError).toBeUndefined();
    // Wait for the clock to actually advance: comparing against a position of
    // zero would prove nothing about continuity either way.
    await waitFor(() => expect(element.currentTime).toBeGreaterThan(0));

    await userEvent.click(canvas.getByRole("button", { name: "Move" }));

    const stage = canvas.getByTestId("stage");
    await waitFor(() => expect(stage.childElementCount).toBe(1));

    // The original node is DETACHED — not moved, not reused. This is the fact
    // that decides the architecture.
    await expect(element.parentElement).toBe(null);

    // And the element now in the destination is a different node that
    // serializes identically, which is exactly how a remount disguises itself.
    const after = canvas.getByTestId("element") as HTMLMediaElement;
    await expect(after).not.toBe(element);

    element.pause();
    after.pause();
  },
};
