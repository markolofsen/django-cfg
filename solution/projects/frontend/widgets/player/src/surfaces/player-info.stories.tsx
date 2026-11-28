import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";
import type { MediaTrack } from "../domain";

import { PlayerInfo } from "./player-info";

/**
 * The metadata popover's contents.
 *
 * Rendered bare here, without the popover around it: what is being specified is
 * WHAT it says, and the popover's own behaviour (that opening it does not
 * recreate the media element) belongs to the dock, which owns the element.
 */

const SONG: MediaTrack = {
  id: "mac-studio:/Users/me/Music/Dikanda/Muzyka Podrozna/07 Nie ma nikogo.mp3",
  kind: "audio",
  src: "blob:mock-audio",
  title: "07 Nie ma nikogo.mp3",
  machineId: "b2aacd578a11b4fb477e7721bd46f912",
  path: "/Users/me/Music/Dikanda/Muzyka Podrozna/07 Nie ma nikogo.mp3",
};

const CLIP: MediaTrack = {
  id: "nuc:/srv/recordings/demo.mp4",
  kind: "video",
  src: "blob:mock-video",
  title: "demo.mp4",
  machineId: "nuc",
  path: "/srv/recordings/demo.mp4",
};

const meta = {
  title: "Widgets/Player/Player info",
  component: PlayerInfo,
  parameters: { layout: "centered" },
  args: { track: SONG },
  decorators: [
    // The popover's real width. A path assertion is meaningless at a width the
    // component never renders at.
    (Story) => <div className="w-80">{Story()}</div>,
  ],
} satisfies Meta<typeof PlayerInfo>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Everything known, which is the case a reader opens this for.
 *
 * The rows are ordered most-identifying first: who made it, then where it is,
 * then what it technically is. Someone opening this is answering "what am I
 * listening to" before "how is it encoded".
 */
export const EverythingKnown: Story = {
  args: {
    machineName: "mac-studio",
    detail: {
      artist: "Dikanda",
      album: "Muzyka Podrozna",
      durationSeconds: 220,
      sizeBytes: 8_400_000,
      codec: "mp3",
    },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("Dikanda")).toBeVisible();
    await expect(canvas.getByText("Muzyka Podrozna")).toBeVisible();
    await expect(canvas.getByText("mac-studio")).toBeVisible();
    // The measurements share one line, so the clock is a substring of it rather
    // than a node of its own.
    await expect(canvas.getByText(/3:40/)).toBeVisible();
  },
};

/**
 * **No raw machine id renders here, ever.**
 *
 * The row this replaces printed `b2aacd578a11b4fb477e7721bd46f912` under the
 * title. That string is correct and useless, and the roster holds a display
 * name for exactly this purpose.
 *
 * MUTANT: fall back to `track.machineId` when no name is known → this fails on
 * the hash, which is the defect the whole seam exists to prevent.
 */
export const AMachineIdNeverReachesTheScreen: Story = {
  args: { machineName: "mac-studio" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("mac-studio")).toBeVisible();
    await expect(canvas.queryByText(/b2aacd578a11b4fb/)).toBeNull();
  },
};

/**
 * A machine the roster no longer knows is NAMED as such.
 *
 * An ordinary state, not an error: a transcript outlives the fleet it names, so
 * a track can perfectly well come from a machine that has since left.
 */
export const AnUnknownMachineSaysSo: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("Unknown machine")).toBeVisible();
    await expect(canvas.queryByText(/b2aacd578a11b4fb/)).toBeNull();
  },
};

/**
 * **A long path keeps its extension**, which is the whole reason this does not
 * use CSS truncation.
 *
 * `text-overflow` can only cut the TAIL, and the tail is where the extension
 * is — so a CSS-truncated path ends `…Muzyka Podr` and the reader cannot tell
 * an `.mp3` from a `.flac`. `elidePathLine` drops whole segments from the head
 * and, at the last resort, elides the middle of the NAME.
 *
 * The full path stays reachable in the title attribute: a truncation with no
 * way to see the value is worse than a long line.
 */
export const ALongPathKeepsItsExtension: Story = {
  args: { machineName: "mac-studio" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const path = await canvas.findByTitle(SONG.path as string);

    await expect(path.textContent ?? "").toMatch(/\.mp3$/);
    await expect(path.textContent ?? "").toContain("…");
    // Shortened by lib-utils, so it must be shorter than what it describes.
    await expect((path.textContent ?? "").length).toBeLessThan((SONG.path as string).length);
  },
};

/**
 * The measurements share ONE line, joined by a middot.
 *
 * As a label/value table each of these spent a whole row stating four
 * characters, which is what made the card tall and left its right half empty.
 * They are all the same KIND of fact, so a reader scans them together rather
 * than looking any one of them up by name — and no label is needed to tell
 * `1920×1080` from `95` from `h264`.
 *
 * MUTANT: give any of them its own labelled row → the single-node assertion
 * fails.
 */
export const TheMeasurementsShareOneLine: Story = {
  args: {
    track: CLIP,
    machineName: "nuc",
    detail: { width: 1920, height: 1080, codec: "h264", durationSeconds: 95 },
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("1920×1080 · h264", { exact: false })).toBeVisible();
    // No label survives for a measurement — those rows are gone entirely.
    await expect(canvas.queryByText("Resolution")).toBeNull();
    await expect(canvas.queryByText("Codec")).toBeNull();
    await expect(canvas.queryByText("Duration")).toBeNull();
  },
};

/**
 * Nothing described yet — the state while the fetch is in flight, and the
 * permanent state for a file nothing can describe.
 *
 * The title and the artwork still render: they come from the track itself,
 * which is always in hand. An empty popover would read as broken. So does the
 * FOOTER, because the path comes from the track too — it is the one fact that
 * never has to be fetched.
 */
export const NothingDescribedYet: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("07 Nie ma nikogo.mp3")).toBeVisible();
    await expect(canvas.getByTitle(SONG.path as string)).toBeVisible();
  },
};

/**
 * The footer takes the FULL path, not the elided line beside it.
 *
 * What is on screen is shortened to fit, and a shortened path pasted into a
 * shell does not resolve. The two strings are different by design, which is
 * exactly the kind of thing that silently regresses.
 */
export const CopyTakesTheWholePath: Story = {
  args: { machineName: "mac-studio" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const copy = await canvas.findByRole("button", { name: "Copy path" });

    // The line is elided; the clipboard value behind it is not.
    const shown = canvas.getByTitle(SONG.path as string).textContent ?? "";
    await expect(shown.length).toBeLessThan((SONG.path as string).length);
    await expect(copy).toBeEnabled();
  },
};

/**
 * The folder is an EXPLICIT act, reached from the footer.
 *
 * The name used to navigate on click, which left the page the reader was on to
 * answer a question they had not asked. Now the name opens this card and going
 * to the tree costs a deliberate second press.
 */
export const TheFolderIsAButton: Story = {
  args: { machineName: "mac-studio", onOpenInFiles: fn() },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.click(await canvas.findByRole("button", { name: "Open folder" }));

    await expect(args.onOpenInFiles).toHaveBeenCalled();
  },
};

/**
 * No reveal target ⇒ no button, rather than one that refuses.
 *
 * Copy still renders: the path is on the card either way, and taking it never
 * depends on the machine being reachable.
 */
export const WithoutARevealTargetOnlyCopyRemains: Story = {
  args: { machineName: "mac-studio" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByRole("button", { name: "Copy path" })).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Open folder" })).toBeNull();
  },
};

/** The machine is a place the reader may want to GO, so its name is a control. */
export const TheMachineIsALink: Story = {
  args: { machineName: "mac-studio", onOpenMachine: fn() },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.click(await canvas.findByRole("button", { name: "mac-studio" }));

    await expect(args.onOpenMachine).toHaveBeenCalled();
  },
};

/**
 * An unknown machine is NOT a link: there is nowhere to go, and a dead control
 * is worse than plain text.
 */
export const AnUnknownMachineIsNotALink: Story = {
  args: { onOpenMachine: fn() },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByText("Unknown machine")).toBeVisible();
    await expect(canvas.queryByRole("button", { name: "Unknown machine" })).toBeNull();
  },
};

/**
 * The footer offers a LINK as well as the path.
 *
 * They are different answers: the path is where the file sits on one machine,
 * the link is how another person opens it. Sharing a path would hand someone a
 * string that means nothing on their own filesystem.
 *
 * The URL is a VALUE built by the shell — this package never assembles a route
 * — and it is copied rather than followed, which is why it arrives as a string
 * at all.
 *
 * MUTANT: drop `shareUrl` from the footer → this fails while every other story
 * stays green.
 */
export const TheFooterSharesALink: Story = {
  args: {
    machineName: "mac-studio",
    shareUrl: "https://console.example/player/mac-studio?path=%2FUsers%2Fme%2Fsong.mp3",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByRole("button", { name: "Copy link" })).toBeEnabled();
    // The path's own copy stays: one takes the value, the other an address.
    await expect(canvas.getByRole("button", { name: "Copy path" })).toBeEnabled();
  },
};

/**
 * No machine ⇒ no address ⇒ no share control.
 *
 * A chat block's inline audio is not a file anyone else can reach, so a button
 * would copy a link that opens nothing. Absent rather than dead.
 */
export const WithoutAMachineThereIsNothingToShare: Story = {
  args: { machineName: "mac-studio" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByRole("button", { name: "Copy path" })).toBeEnabled();
    await expect(canvas.queryByRole("button", { name: "Copy link" })).toBeNull();
  },
};
