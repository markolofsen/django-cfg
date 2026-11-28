import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';

import { LayoutI18nProvider, LocaleSwitcher } from '@djangocfg/layouts';

const LOCALES = ['en', 'ru'];

function Host({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState('ru');
  return (
    <LayoutI18nProvider value={{ locale, locales: LOCALES, onLocaleChange: setLocale }}>
      {children}
    </LayoutI18nProvider>
  );
}

const meta = {
  title: 'Packages/Layouts/LocaleSwitcher',
  component: LocaleSwitcher,
  parameters: { layout: 'centered' },
  decorators: [(Story) => <Host><Story /></Host>],
} satisfies Meta<typeof LocaleSwitcher>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { buttonVariant: 'outline', size: 'default' },
};

/** The flag keeps its own size while the button stretches to a 44px touch target. */
export const IconInTouchTarget: Story = {
  args: {
    variant: 'dropdown',
    buttonVariant: 'ghost',
    size: 'icon',
    className: 'size-11 rounded-full p-0',
  },
};

export const IconDialogInTouchTarget: Story = {
  args: {
    variant: 'dialog',
    buttonVariant: 'outline',
    size: 'icon',
    className: 'size-11 rounded-full p-0',
  },
};
