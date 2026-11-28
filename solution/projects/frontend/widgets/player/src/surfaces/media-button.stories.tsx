import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";
import type { MediaTrack } from "../domain";

import { MediaButton } from "./media-button";

/**
 * The shared playable-file control, used by the chat transcript and the Files
 * viewer.
 *
 * These stories pin the property the whole package rests on: **it mounts nothing
 * that can make sound**, for every kind. A transcript holding several of these
 * still holds zero media elements.
 */

const SONG: MediaTrack = {
  id: "mac-studio:/Users/me/Sanya.mp3",
  kind: "audio",
  src: "/api/admin/machines/mac-studio/files/download?path=%2FUsers%2Fme%2FSanya.mp3",
  title: "Sanya.mp3",
  machineId: "mac-studio",
  path: "/Users/me/Music/Sanya.mp3",
};

const CLIP: MediaTrack = {
  id: "mac-studio:/Users/me/demo.mp4",
  kind: "video",
  src: "/api/admin/machines/mac-studio/files/download?path=%2FUsers%2Fme%2Fdemo.mp4",
  title: "demo.mp4",
  machineId: "mac-studio",
  path: "/Users/me/Movies/demo.mp4",
};

const meta = {
  title: "Widgets/Player/Media button",
  component: MediaButton,
  parameters: { layout: "padded" },
  args: { track: SONG, active: false, onPlay: () => undefined },
} satisfies Meta<typeof MediaButton>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * The row names the file and the folder it sits in, and offers one action.
 *
 * The raw machine id and the absolute path are NOT shown: they ate half the
 * width and answered a question nobody asked — the reader just said "play this".
 * Asserted as an absence, so restoring them fails here.
 */
export const OffersToPlay: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("Sanya.mp3")).toBeVisible();
    // The last folder only — enough to tell two copies apart, and no more.
    await expect(canvas.getByText("Music")).toBeVisible();
    await expect(canvas.queryByText(/mac-studio/)).toBeNull();
    await expect(canvas.queryByText(/\/Users\/me/)).toBeNull();
  },
};

/**
 * **Video mounts nothing either. This is the Phase 4 change.**
 *
 * The card this replaces mounted a real video player once its file became the
 * active track — the one path by which a transcript owned an element, and
 * therefore the one by which navigating away killed a video. The stage answers
 * the need that exception existed for.
 */
export const VideoMountsNoElementEvenWhenActive: Story = {
  args: { track: CLIP, active: true },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("demo.mp4")).toBeVisible();
    // The assertion that IS the phase: nothing here can make sound or show a
    // picture, whether or not this file is the active track.
    await expect(canvasElement.querySelector("video")).toBeNull();
    await expect(canvasElement.querySelector("audio")).toBeNull();
  },
};

/** Audio mounts nothing either, active or not — the rule has no exceptions now. */
export const AudioMountsNoElement: Story = {
  args: { active: true },
  play: async ({ canvasElement }) => {
    await expect(canvasElement.querySelector("audio")).toBeNull();
    await expect(canvasElement.querySelector("video")).toBeNull();
  },
};

/** Clicking asks the host to play it. An intent — the row loads nothing itself. */
export const ClickingAsksTheHost: Story = {
  args: { onPlay: fn() },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    await userEvent.click(await canvas.findByRole("button"));
    await expect(args.onPlay).toHaveBeenCalledTimes(1);
  },
};

/**
 * The active file says so, and says it as STATE rather than as a second control.
 *
 * `aria-pressed` carries it for a screen reader; the label carries it visually.
 */
export const ActiveFileIsMarked: Story = {
  args: { active: true },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const row = await canvas.findByRole("button");
    await expect(row).toHaveAttribute("aria-pressed", "true");
    await expect(canvas.getByText("Now playing")).toBeVisible();
  },
};

/**
 * No artwork: a placeholder TILE, not a bare icon and not a broken image.
 *
 * Most files carry no embedded art, so this is the common view and has to look
 * deliberate — an empty square of the right size keeps every row the same shape.
 */
export const WithoutArtwork: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByTestId("track-cover-placeholder")).toBeVisible();
    await expect(canvasElement.querySelector("img")).toBeNull();
  },
};

/**
 * Artwork that fails to load falls back to the tile.
 *
 * The cover URL points at the relay's cover route, which 404s for a file whose
 * art was stripped and fails outright when the machine goes away. Without the
 * fallback the row shows a broken-image glyph — an error, where the honest
 * answer is "this file has no picture".
 */
export const ArtworkThatFailsToLoad: Story = {
  args: { track: { ...SONG, poster: "/does-not-exist.png" } },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    // MUTANT: drop `onError` in `TrackCover` → this times out with a broken
    // <img> still in the DOM.
    await expect(await canvas.findByTestId("track-cover-placeholder")).toBeVisible();
  },
};

/**
 * A file with no path at all — a remote URL, or one the block did not name.
 *
 * The folder line is absent rather than empty: a blank second row makes every
 * card taller for a fact that does not exist.
 */
export const WithoutAFolder: Story = {
  args: { track: { id: "x", kind: "audio", src: "https://example.com/a.mp3", title: "a.mp3" } },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("a.mp3")).toBeVisible();
    await expect(canvas.queryByTestId("track-cover-placeholder")).toBeVisible();
  },
};
