import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, userEvent, waitFor, within } from "storybook/test";

import { MediaElement } from "./media-element";
import { silentWavDataUrl } from "./media-fixture";

/**
 * The shape that replaced the portal: the element is mounted ONCE, in one
 * place, and never moves. Surfaces change the box around it.
 *
 * [portal-move.stories.tsx](./portal-move.stories.tsx) shows why: changing a
 * portal's container recreates the element rather than re-parenting it, which
 * reloads the source and restarts playback. So the element cannot be what
 * travels between surfaces.
 *
 * What travels instead is its GEOMETRY. The element keeps one DOM position for
 * the life of a track, and each surface says where on screen it should appear —
 * docked in the footer, filling a route, or hidden entirely when only audio
 * matters. This story proves the property the portal could not deliver: a
 * playing track survives every surface change, because nothing about the
 * element's mounting changed.
 */

const SRC = silentWavDataUrl();

type Surface = "dock" | "stage" | "hidden";

/**
 * The dimensions each surface asks for. Data, not branches: a surface is a
 * description of a box, and adding one must not mean editing a component.
 */
const SURFACE_STYLE: Record<Surface, React.CSSProperties> = {
  dock: { position: "fixed", right: 16, bottom: 16, width: 240, height: 48 },
  stage: { position: "fixed", inset: 0, width: "100%", height: "100%" },
  hidden: { position: "fixed", width: 1, height: 1, opacity: 0 },
};

function StableMountHarness() {
  const [surface, setSurface] = useState<Surface>("dock");
  const surfaces: readonly Surface[] = ["dock", "stage", "hidden"];

  return (
    <div>
      <button
        type="button"
        onClick={() => {
          const el = document.querySelector<HTMLMediaElement>("[data-testid='element']");
          if (el === null) return;
          void el.play().catch((cause: unknown) => {
            el.dataset.playError = cause instanceof Error ? cause.name : String(cause);
          });
        }}
      >
        Start
      </button>
      {surfaces.map((name) => (
        <button key={name} type="button" onClick={() => setSurface(name)}>
          {name}
        </button>
      ))}
      {/* ONE mount point, never conditional, never keyed on the surface. Both
          would recreate the element and restart the track. The surface decides
          the BOX; the element inside it is untouched. */}
      <div data-testid="frame" style={SURFACE_STYLE[surface]}>
        <MediaElement
          kind="audio"
          src={SRC}
          data-testid="element"
          preload="auto"
          style={{ width: "100%", height: "100%" }}
          // A media element that never loads reports NOTHING: no error event, no
          // rejection — `readyState` simply stays 0 and the clock never moves, so
          // the assertion below fails as a bare `expect(0).toBeGreaterThan(0)`
          // that says nothing about why.
          //
          // These record the two facts that distinguish the cases. Measured: a
          // browser without media decoding stalls here on a VALID file — the
          // same 30s WAV that WebAudio's `decodeAudioData` accepts, and that the
          // Playwright Chromium this suite runs in plays fine.
          onLoadedMetadata={(event) => {
            event.currentTarget.dataset.loaded = "yes";
          }}
          onError={(event) => {
            event.currentTarget.dataset.loadError = String(event.currentTarget.error?.code ?? "none");
          }}
        />
      </div>
    </div>
  );
}

const meta = {
  title: "Widgets/Player/Element / Stable mount",
  component: StableMountHarness,
  parameters: { layout: "padded" },
} satisfies Meta<typeof StableMountHarness>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Playback survives every surface change, and the element is never recreated.
 *
 * The identity assertion is the load-bearing one. A story that only checked
 * `currentTime` would pass against a recreated element on a machine slow enough
 * that the new element had already buffered and advanced.
 */
export const PlaybackSurvivesEverySurface: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const element = (await canvas.findByTestId("element")) as HTMLMediaElement;

    // The fixture must actually DECODE before anything below means anything. A
    // browser whose media pipeline is disabled stalls at `readyState` 0 with no
    // error and no rejection, and every later assertion then fails as a bare
    // `expect(0).toBeGreaterThan(0)` that names no cause. This says the cause.
    await waitFor(() =>
      expect(
        element.dataset.loaded ?? `not decoded (readyState ${element.readyState}, error ${element.dataset.loadError ?? "none"})`,
      ).toBe("yes"),
    );

    await userEvent.click(canvas.getByRole("button", { name: "Start" }));
    await expect(element.dataset.playError).toBeUndefined();
    await waitFor(() => expect(element.currentTime).toBeGreaterThan(0));

    for (const name of ["stage", "hidden", "dock"] as const) {
      const before = element.currentTime;
      await userEvent.click(canvas.getByRole("button", { name }));

      // The SAME node after every change. This is what the portal could not do.
      await expect(canvas.getByTestId("element")).toBe(element);
      await expect(element.parentElement).toBe(canvas.getByTestId("frame"));
      // The clock never went backwards, so the source was never reloaded.
      await expect(element.currentTime).toBeGreaterThanOrEqual(before);
      await expect(element.paused).toBe(false);
    }

    element.pause();
  },
};
