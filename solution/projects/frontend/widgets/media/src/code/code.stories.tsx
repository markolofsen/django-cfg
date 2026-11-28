import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, within } from "storybook/test";

import { Code } from "./code";

/**
 * A read-only code listing.
 *
 * Replaces the retired `@djangocfg/ui-tools/pretty-code`, which ran Prism while the rest of
 * this console runs shiki. One highlighter means one theme to keep matched and
 * one answer to "is this language supported".
 *
 * The two variants are the interesting part: `card` is its own surface, `plain`
 * embeds in a container that already scrolls and already owns the copy control.
 */
const meta = {
  title: "Widgets/Media/Code",
  component: Code,
  parameters: { a11y: { test: "error" } },
} satisfies Meta<typeof Code>;

export default meta;
type Story = StoryObj<typeof meta>;

const SNIPPET = `export function greet(name: string): string {
  return \`hello, \${name}\`;
}`;

/** A standalone listing: border, ground, copy and download controls. */
export const Card: Story = {
  args: { data: SNIPPET, language: "typescript" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole("button", { name: /copy/i })).toBeInTheDocument();
  },
};

/**
 * Chrome-less, for embedding.
 *
 * No copy control and no height cap: the parent scrolls, and a second scroll
 * surface here would trap the wheel between them.
 */
export const Plain: Story = {
  args: { data: SNIPPET, language: "typescript", variant: "plain" },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.queryByRole("button", { name: /copy/i })).toBeNull();
  },
};

/** The wizard's density — 12px against the card's 14px. */
export const Compact: Story = {
  args: { data: SNIPPET, language: "typescript", size: "sm" },
};

/**
 * A source that contains its own fence.
 *
 * The listing is built by wrapping the source in a markdown fence, so a README
 * or an agent answer carrying ``` would end the block early and render its tail
 * as prose. The wrapper widens the fence past the longest run inside.
 */
export const ContainsAFence: Story = {
  args: {
    data: "before\n```\ninner\n```\nafter",
    language: "markdown",
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText(/after/)).toBeInTheDocument();
  },
};
