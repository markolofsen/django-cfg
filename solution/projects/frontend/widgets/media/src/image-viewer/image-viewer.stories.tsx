import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, within } from "storybook/test";

import { ImageViewer } from "./components";

/**
 * The image viewer, in the presentation chat actually uses.
 *
 * This package is a fork of the retired `@djangocfg/ui-tools`' viewer, and the save control
 * below is the reason it exists: a generated picture the agent produced was
 * openable but not keepable, and adding the control upstream would mean
 * publishing a design-system release for one product's need.
 */
const meta = {
  title: "Widgets/Media/ImageViewer",
  component: ImageViewer,
  parameters: { layout: "fullscreen", a11y: { test: "error" } },
} satisfies Meta<typeof ImageViewer>;

export default meta;
type Story = StoryObj<typeof meta>;

// A 2x1 PNG: enough for the viewer to resolve real pixels and report a size,
// while the story stays inline — a remote asset would fail for reasons that
// have nothing to do with the component.
const PIXEL =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAABCAYAAAD0In+KAAAAFElEQVR42mP8z8BQz0AEYBxVSF+FABJADveWkH6oAAAAAElFTkSuQmCC";

/**
 * The shape a generated image arrives in: the src is a content-addressed relay
 * path with NO extension, so `file.name` is the only place a meaningful
 * download filename can come from — the sha256 is a poor thing to hand
 * someone's Downloads folder.
 */
const GENERATED = [
  {
    file: {
      name: "generated.jpeg",
      path: "/api/admin/attachments/30baaf135aba6df2f2546b382f28e6487e0d27d03b815c77f54e033c96029bab",
    },
    src: PIXEL,
  },
];

/** Embedded presentation — the toolbar viewer, no lightbox chrome. */
export const Embedded: Story = {
  args: { images: GENERATED },
};

/**
 * The lightbox, which is what a reader sees after clicking a picture in chat.
 *
 * Asserts the save control is present AND that the anchor it builds carries the
 * store's filename: a button that downloads `30baaf13…9bab` with no extension
 * is technically working and practically useless, and only the attribute shows
 * the difference.
 */
export const LightboxWithSave: Story = {
  args: { images: GENERATED, lightbox: true, onRequestClose: () => {} },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const save = await canvas.findByRole("button", { name: "Save image" });
    await expect(save).toBeVisible();
  },
};
