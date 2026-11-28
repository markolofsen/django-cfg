import type { Meta, StoryObj } from '@storybook/react-vite';

import { LocaleSuggestionView } from './LocaleSuggestionView';

const meta = {
  title: 'Packages/Layouts/LocaleSuggestion',
  component: LocaleSuggestionView,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component:
          'The hint card `BaseApp` shows when the browser language is a site locale other than the current one. It is written in the visitor\'s language and names the target in its own. The decision and the memory are covered by unit tests; this renders the view.',
      },
    },
  },
  decorators: [(Story) => <div className="relative h-72 bg-background"><Story /></div>],
  args: { browserLanguage: 'de-DE', target: 'de', onSwitch: () => {}, onDismiss: () => {} },
} satisfies Meta<typeof LocaleSuggestionView>;

export default meta;
type Story = StoryObj<typeof meta>;

export const German: Story = {};

export const Japanese: Story = { args: { browserLanguage: 'ja', target: 'ja' } };

/** An Arabic reader on an English page: the card is right-to-left, the page is not. */
export const ArabicRtl: Story = { args: { browserLanguage: 'ar', target: 'ar' } };

/** A language with no bundled copy falls back to English, still naming the target natively. */
export const UnbundledLanguage: Story = { args: { browserLanguage: 'cs', target: 'cs' } };
