import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, waitFor, within } from "storybook/test";

import { TrackCover } from "./track-cover";

/**
 * The track's artwork, and what stands in when there is none.
 *
 * Most audio files carry no embedded cover, so the fallback is the DEFAULT view
 * rather than an error state — which is exactly why it had gone unspecified,
 * and why the console showed the same `.mp3` as a branded mark in a chat chip
 * and a grey Lucide note in the player two rows below it.
 */

const ARTWORK =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='96' height='96'%3E%3Crect width='96' height='96' fill='%23c2410c'/%3E%3C/svg%3E";

const meta = {
  title: "Widgets/Player/Track cover",
  component: TrackCover,
  parameters: { layout: "centered" },
  args: { kind: "audio", size: 64 },
} satisfies Meta<typeof TrackCover>;

export default meta;
type Story = StoryObj<typeof meta>;

/** A file that HAS artwork shows it, and no placeholder is drawn. */
export const ArtworkWins: Story = {
  args: { src: ARTWORK, path: "/Users/me/Music/song.mp3" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByRole("presentation")).toHaveAttribute("src", ARTWORK);
    await expect(canvas.queryByTestId("track-cover-placeholder")).toBeNull();
  },
};

/**
 * **No artwork ⇒ the console's TYPED file glyph**, not a generic note.
 *
 * The same file appears in a chat chip, in the chat's reference card and here;
 * all three now ask the same file-glyph question, so they cannot
 * answer it differently. The glyph loads behind a lazy boundary (the icon set
 * is 476 KB), so the assertion waits for the chunk rather than for a frame.
 *
 * MUTANT: draw a `lucide/Music` here instead → the typed glyph never arrives
 * and this fails.
 */
export const WithoutArtworkTheGlyphIsTyped: Story = {
  args: { path: "/Users/me/Music/song.mp3" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const tile = await canvas.findByTestId("track-cover-placeholder");

    // Asserting on a bare `svg` would pass for a Lucide note too — measured,
    // and the mutation went undetected. The icon set wraps its mark in a sized
    // `span` that Lucide does not, so THAT is the discriminator.
    // A generous timeout, not the 1s default: the icon set is a 476 KB lazy
    // chunk, and under a full parallel run it arrives well after the frame that
    // renders the Suspense fallback. Measured — this story is green in
    // isolation and flaked only alongside the rest of the suite.
    await waitFor(async () => {
      const wrapper = tile.querySelector("span[aria-hidden]");
      await expect(wrapper).not.toBeNull();
      await expect(wrapper?.querySelector("svg")).not.toBeNull();
    }, { timeout: 10_000 });
  },
};

/**
 * A track with no PATH names the medium instead.
 *
 * A URL or data source has no extension to type from, so there is nothing for
 * the table to look up — and a generic document would say less than "this is
 * sound". The one case the medium glyph still exists for.
 */
export const WithoutAPathTheMediumIsNamed: Story = {
  args: { kind: "video" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByTestId("track-cover-placeholder")).toBeVisible();
  },
};

/**
 * A cover that 404s falls back to the tile, not to a broken-image glyph.
 *
 * The relay's cover route can fail for a file whose art was stripped, or when
 * the machine goes away mid-transcript. "This file has no picture" is the
 * honest answer; a broken image reads as a defect.
 */
export const AFailedCoverFallsBackToTheTile: Story = {
  args: { src: "https://example.invalid/missing.png", path: "/Users/me/Music/song.mp3" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(async () => {
      await expect(await canvas.findByTestId("track-cover-placeholder")).toBeVisible();
    });
  },
};

/** The tile is one fixed size in every state, so a row never resizes under the cursor. */
export const TheTileIsOneSizeInEveryState: Story = {
  args: { path: "/Users/me/Music/song.mp3", size: 36 },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const tile = await canvas.findByTestId("track-cover-placeholder");
    const { width, height } = tile.getBoundingClientRect();

    await expect(Math.round(width)).toBe(36);
    await expect(Math.round(height)).toBe(36);
  },
};

