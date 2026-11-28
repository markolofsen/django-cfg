import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, fn, userEvent, within } from "storybook/test";

import { SeekBar } from "./seek-bar";

/**
 * The row's progress meter, made live.
 *
 * Every story names a user-visible STATE rather than the props that produce it
 * (`@rules/general/executable-ui-specifications.md`). The component is pure — position
 * and duration in, scrub intents out — so each state is reachable with no store
 * and no media element.
 */

const noop = () => undefined;

const meta = {
  title: "Widgets/Player/Seek bar",
  component: SeekBar,
  parameters: { layout: "padded" },
  args: {
    position: 64,
    duration: 220,
    // Ahead of the playhead but short of the end — the state a streamed file is
    // in for most of its life, and the only one in which the buffered range is
    // distinguishable from both an empty bar and a full one.
    buffered: 130,
    onScrubStart: noop,
    onScrubMove: noop,
    onScrubEnd: noop,
  },
  decorators: [
    // The bar takes its width from the row it lives in, so a story that let it
    // size to content would assert against a geometry it never has.
    (Story) => <div className="w-96">{Story()}</div>,
  ],
} satisfies Meta<typeof SeekBar>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Playing, part-way through — the state the bar spends its life in.
 *
 * The accessible value is a TIME, not a count of seconds: the control is a bar,
 * and "64" tells a screen-reader user nothing they can act on.
 */
export const PartWayThrough: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const slider = await canvas.findByRole("slider", { name: "Seek" });

    await expect(slider).toHaveAttribute("aria-valuetext", "1:04 / 3:40");
    await expect(slider).toBeEnabled();
  },
};

/**
 * **The accessible name and value live on the THUMB**, which is where Radix
 * puts `role="slider"`.
 *
 * A label left on the Root names a generic element and the control itself stays
 * anonymous — this was real, and it affected every slider in the console until
 * the primitive started forwarding these. The query above finds the control by
 * role AND name, so it fails if either moves.
 *
 * MUTANT: drop the `aria-label` forwarding in ui-core → this fails.
 */
export const TheControlIsNamedForScreenReaders: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const slider = await canvas.findByRole("slider", { name: "Seek" });

    await expect(slider).toHaveAttribute("data-slot", "slider-thumb");
  },
};

/**
 * A file whose length is unknown cannot be moved through.
 *
 * Before metadata arrives `duration` is zero, and a bar that accepted a drag
 * then would be asking the reader to aim at a scale that does not exist yet.
 * DISABLED rather than hidden: the row keeps its shape, and the control appears
 * where it will be.
 */
export const UnknownLengthIsNotSeekable: Story = {
  args: { duration: 0, position: 12, buffered: 0 },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const slider = await canvas.findByRole("slider", { name: "Seek" });

    // Radix marks the state with `data-disabled` on the thumb rather than with
    // the `disabled` attribute, which is what a form control would use.
    await expect(slider).toHaveAttribute("data-disabled");
    // No total to state, so the read-out is the elapsed time alone rather than
    // a fraction with a meaningless denominator.
    await expect(slider).toHaveAttribute("aria-valuetext", "0:12");
  },
};

/**
 * **The drag wins while it lasts.**
 *
 * The element keeps playing under the finger, so its clock and the pointer are
 * two writers of one number. This is the render half of the guard: while
 * `scrubbing`, the bar shows where the FINGER is and ignores the playhead.
 * Without it the thumb snaps back between pointer moves.
 *
 * MUTANT: render `position` unconditionally → the value follows the playhead
 * and this fails.
 */
export const DraggingShowsTheFingerNotThePlayhead: Story = {
  args: { scrubbing: true, scrubPosition: 180, position: 64 },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const slider = await canvas.findByRole("slider", { name: "Seek" });

    await expect(slider).toHaveAttribute("aria-valuenow", "180");
    await expect(slider).toHaveAttribute("aria-valuetext", "3:00 / 3:40");
  },
};

/**
 * The first change of a gesture is the GRAB, not a move.
 *
 * Radix fires `onValueChange` for a click on the track too, and that has no
 * pointerdown-on-thumb to hook — so the drag is opened on the first change and
 * closed by the commit, which makes a plain click a one-move drag.
 */
export const AClickStartsAScrub: Story = {
  args: { onScrubStart: fn(), onScrubMove: fn() },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const slider = await canvas.findByRole("slider", { name: "Seek" });

    slider.focus();
    // A keyboard step goes through the same `onValueChange` a pointer does.
    await userEvent.type(slider, "{ArrowRight}");

    await expect(args.onScrubStart).toHaveBeenCalled();
    // Not yet a MOVE: the gesture has only just opened.
    await expect(args.onScrubMove).not.toHaveBeenCalled();
  },
};

/**
 * A failure mutes the bar.
 *
 * A range still creeping forward under "the machine went offline" is exactly
 * the looks-healthy-while-silent shape this package exists to remove.
 */
export const AFailureMutesTheRange: Story = {
  args: { failed: true },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await canvas.findByRole("slider", { name: "Seek" });
    const range = canvasElement.querySelector("[data-slot=slider-range]");

    await expect(range).not.toBeNull();
    await expect(range).toHaveClass("bg-destructive");
  },
};


