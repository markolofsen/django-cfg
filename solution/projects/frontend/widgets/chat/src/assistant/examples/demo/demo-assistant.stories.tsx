import type { Meta, StoryObj } from '@storybook/react-vite';

import '../../../styles/index.css';

import { DemoAssistant } from './demo-assistant';

/**
 * The complete assistant, and the only one: every feature is on and every placement is a story of this same component, so there is no second, partial copy to drift.
 * Try: type "question", "approve a change", "table" or "picture" (an inline picture; click it); attach a picture and click it; open History (twelve older chats, search); switch the model chip; add a file named `fail.txt`.
 * The failure and edge states of the chat are in `Widgets/Assistant/States`; the assistant inside a real page is `Layouts/Notion shell`.
 */
const meta = {
  title: 'Widgets/Chat/Assistant/Complete',
  component: DemoAssistant,
  parameters: { layout: 'padded' },
  decorators: [(Story) => <div className="mx-auto max-w-md"><Story /></div>],
} satisfies Meta<typeof DemoAssistant>;
export default meta;
type Story = StoryObj<typeof meta>;

/** A long stored thread: metrics, a table, code, steps, an approval card, media and files; History and every control are live. */
export const Default: Story = {};
/** No history: the greeting and four starter prompts, each leading to a different kind of block. */
export const Empty: Story = { args: { empty: true } };
/** The tablet's floating window (no backdrop; the page stays usable). Use the Tablet viewport. */
export const Dock: Story = { args: { placement: 'dock' }, parameters: { layout: 'fullscreen', viewport: { defaultViewport: 'tablet' } }, decorators: [(Story) => <Story />] };
/** The phone's full-screen sheet; it slides up. Use the Phone viewport. */
export const Sheet: Story = { args: { placement: 'sheet' }, parameters: { layout: 'fullscreen', viewport: { defaultViewport: 'mobile1' } }, decorators: [(Story) => <Story />] };
