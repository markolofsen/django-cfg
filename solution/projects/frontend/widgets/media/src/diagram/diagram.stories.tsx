import type { Meta, StoryObj } from "@storybook/react-vite";
import { expect, within } from "storybook/test";

import { Diagram } from "./diagram";

/**
 * A mermaid diagram, drawn from source the agent wrote.
 *
 * The renderer is `beautiful-mermaid` rather than the mermaid runtime: 2.5 MB
 * against 84 MB, and no DOM at all, which is what lets the same code be tested
 * without a browser and rendered here.
 *
 * The three stories are the three states a reader can actually meet, and the
 * two fallbacks are the interesting ones — both show the SOURCE, because an
 * undrawable diagram is still the answer the agent gave.
 */
const meta = {
  title: "Widgets/Media/Diagram",
  component: Diagram,
  parameters: { a11y: { test: "error" } },
} satisfies Meta<typeof Diagram>;

export default meta;
type Story = StoryObj<typeof meta>;

const FLOWCHART = `graph TD
  A[Agent] --> B{Tool call}
  B -->|allowed| C[Run]
  B -->|denied| D[Explain]
  C --> E[Answer]
  D --> E`;

/** The ordinary case: a finished diagram becomes a picture. */
export const Rendered: Story = {
  args: { chart: FLOWCHART },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    // The role, not the tag: the wrapper is what carries the accessible name,
    // and a reader meets the diagram through that name or not at all.
    await expect(canvas.getByRole("img")).toBeInTheDocument();
  },
};

/**
 * Mid-stream, the source shows instead.
 *
 * Not a loading spinner, and not a partial picture: the renderer does not fail
 * on half-arrived source, it draws a plausible WRONG diagram that changes with
 * every token. Holding the source back until the shape closes is what stops a
 * reader watching a diagram assert three different things in a row.
 */
export const Streaming: Story = {
  args: { chart: "graph TD\n  A[Agent] --> ", streaming: true },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.queryByRole("img")).toBeNull();
    await expect(canvas.getByText(/graph TD/)).toBeInTheDocument();
  },
};

/**
 * A diagram type the parser does not cover.
 *
 * `pie` is the measured example — the parser handles flowchart, sequence,
 * state, class and ER, and rejects the rest by header. The fallback is the
 * same as the streaming one on purpose: an error box would replace the answer
 * with a complaint about our renderer.
 */
export const UnsupportedType: Story = {
  args: { chart: 'pie title Votes\n  "Yes" : 70\n  "No" : 30' },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.queryByRole("img")).toBeNull();
    await expect(canvas.getByText(/pie title Votes/)).toBeInTheDocument();
  },
};

/**
 * A diagram the model painted itself.
 *
 * THE case to look at in both themes, and the one four rounds of screenshots
 * were spent on. An authored `fill:#4285F4` reaches the SVG as a literal while
 * the label is a variable, so the two halves answer to different themes; each
 * authored colour is therefore re-tinted onto a token PAIR.
 *
 * Two properties are visible here and in no test:
 *
 * - the peer branches are ONE tint. The model wrote `#5C9EFF` and `#4285F4` —
 *   hues one degree apart — and keying on the literal made them two groups, so
 *   equal-looking boxes carried different label colours.
 * - the decision diamond is a DIFFERENT tint, because its hue genuinely
 *   differs. Flattening everything to one colour would also pass "no hex".
 */
export const AuthorPainted: Story = {
  args: {
    chart: [
      'graph TD;',
      '    A[Начало] --> B{Вопрос}',
      '    B -->|да| C[Решение А]',
      '    B -->|нет| D[Решение B]',
      '    C --> E[Финал]',
      '    D --> E',
      '    style A fill:#4285F4,color:#fff',
      '    style B fill:#f5f5f5',
      '    style C fill:#5C9EFF',
      '    style D fill:#4285F4',
      '    style E fill:#4285F4',
    ].join('\n'),
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByRole('img')).toBeInTheDocument();
  },
};
