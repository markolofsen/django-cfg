import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, within } from "storybook/test";

import { Markdown } from "./markdown";

/**
 * Markdown a reader is shown, outside any conversation.
 *
 * Sibling to chat's `Response`. Both wrap streamdown; they differ on who wrote
 * the text. `Response` renders the user's own agent and grants an app
 * scheme; this one renders a news post or a file and grants no app scheme.
 */
const meta = {
  title: "Widgets/Media/Markdown",
  component: Markdown,
  parameters: { a11y: { test: "error" } },
} satisfies Meta<typeof Markdown>;

export default meta;
type Story = StoryObj<typeof meta>;

const DOCUMENT = `## Release 2.4

Adds a **diagram renderer** and retires the old markdown path.

| Surface | Before | After |
|---|---|---|
| transcript | code block | diagram |
| document | Prism | shiki |

See the [changelog](https://example.com/changelog) for the rest.`;

export const Document: Story = {
  args: { children: DOCUMENT },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    // GFM is what made the replacement safe — a news post is mostly tables.
    await expect(canvas.getByRole("table")).toBeInTheDocument();
    await expect(canvas.getByRole("link", { name: /changelog/i })).toBeInTheDocument();
  },
};

/** Body scale. Headings track it a notch above. */
export const Compact: Story = {
  args: { children: DOCUMENT, size: "xs" },
};

/**
 * Raw HTML arrives as TEXT.
 *
 * A deliberate difference from the predecessor, which parsed HTML and then
 * sanitized it. `<script>` cannot execute — and `<strong>` does not emphasise
 * either, which is the half worth seeing before writing a catalogue document.
 */
export const RawHtmlIsShownAsText: Story = {
  args: { children: "Written as <strong>bold</strong>, shown as tags." },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText(/<strong>/)).toBeInTheDocument();
  },
};
