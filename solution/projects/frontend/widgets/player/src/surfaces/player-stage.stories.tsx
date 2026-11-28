import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, within } from "storybook/test";
import type { MediaTrack } from "../domain";

import { PlayerStage } from "./player-stage";

/**
 * The stage — the route where a track is watched full-size.
 *
 * Every story asserts something the stage OWNS. It deliberately has no
 * transport, no title bar and no element: the dock's row is still on screen
 * underneath and carries all three, because two transports for one track is the
 * defect this package exists to remove.
 */

const CLIP: MediaTrack = {
  id: "mac-studio:/Users/me/demo.mp4",
  kind: "video",
  src: "blob:mock-video",
  title: "demo.mp4",
  machineId: "mac-studio",
  path: "~/Movies",
};

const SONG: MediaTrack = {
  id: "mac-studio:/Users/me/Sanya.mp3",
  kind: "audio",
  src: "blob:mock-audio",
  title: "Sanya.mp3",
  machineId: "mac-studio",
  path: "~/Music",
};

const meta = {
  title: "Widgets/Player/Player stage",
  component: PlayerStage,
  parameters: { layout: "fullscreen" },
  args: { track: CLIP },
  decorators: [
    // The stage fills its route, so it needs a bounded height to lay out at all.
    (Story) => <div style={{ height: "480px" }}><Story /></div>,
  ],
} satisfies Meta<typeof PlayerStage>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * A video: the stage draws NOTHING, on purpose.
 *
 * The dock's frame is already covering this area with the real element. A
 * placeholder underneath would show through while the frame resizes and read as
 * a second, broken player — so the honest answer is an empty region.
 */
export const VideoDrawsNothing: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    // The landmark exists, so the route is not anonymous to a screen reader.
    await expect(await canvas.findByRole("region", { name: "Player" })).toBeVisible();
    // No element and no artwork: both would be a second thing claiming to play.
    await expect(canvas.queryByTestId("player-stage-artwork")).toBeNull();
    await expect(canvasElement.querySelector("video")).toBeNull();
    await expect(canvasElement.querySelector("audio")).toBeNull();
  },
};

/**
 * Audio reached through a delivered link draws NOTHING here — cover art or not.
 *
 * The stage is offered only for video (`canOpenStage`), so its artwork branch
 * was code no route could reach. Reviving it would give audio a second
 * full-screen answer competing with the row and the metadata popover, which is
 * the duplication this design removed: the file's name was measured appearing
 * four times on one screen.
 *
 * Artwork is not lost by this — it is on the ROW at every moment, and larger in
 * the popover, both without leaving the page.
 */
export const AudioDrawsNothingEvenWithArtwork: Story = {
  args: { track: { ...SONG, poster: "data:image/gif;base64,R0lGODlhAQABAAAAACw=" } },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByRole("region", { name: "Player" })).toBeVisible();
    await expect(canvas.queryByTestId("player-stage-artwork")).toBeNull();
    await expect(canvasElement.querySelector("img")).toBeNull();
  },
};

/**
 * A stale deep link: the address names the stage, nothing is loaded.
 *
 * A REAL state, not an error — the stage has its own address, so it opens on a
 * cold load. It says so in words.
 */
export const NothingIsPlaying: Story = {
  args: { track: null },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("Nothing is playing")).toBeVisible();
    await expect(canvas.queryByTestId("player-stage-artwork")).toBeNull();
  },
};
