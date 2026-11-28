import type { Meta, StoryObj } from "@storybook/react-vite";

import {
  CardLoadingFallback,
  InlineLoadingFallback,
  LoadingFallback,
  MapLoadingFallback,
  Spinner,
} from "./lazy-wrapper";

/**
 * What a dynamically imported surface shows while its chunk loads.
 *
 * Forty-odd tools share these, so they are deliberately quiet: a reserved
 * height so the page does not jump when the real surface lands, and a
 * `currentColor` spinner so the caller sets the tone.
 */
const meta = {
  title: "Widgets/Kit/Loading placeholders",
  component: LoadingFallback,
  args: { minHeight: 160 },
} satisfies Meta<typeof LoadingFallback>;

export default meta;
type Story = StoryObj<typeof meta>;

/** The block placeholder; `showText` adds the caption. */
export const Block: Story = {};

export const WithText: Story = { args: { showText: true } };

/** Every placeholder side by side, at the sizes the tools use them. */
export const Gallery: Story = {
  render: () => (
    <div className="grid gap-6 sm:grid-cols-2">
      <div className="flex items-center gap-3 text-muted-foreground">
        <Spinner />
        <span className="text-sm">Spinner</span>
      </div>
      <InlineLoadingFallback />
      <LoadingFallback minHeight={160} showText />
      <CardLoadingFallback title="Loading the editor" description="This takes a moment the first time." minHeight={160} />
      <MapLoadingFallback minHeight={160} />
    </div>
  ),
};
