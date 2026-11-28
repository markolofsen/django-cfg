import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Switch, Label } from '@djangocfg/ui-core/components';

const meta: Meta<typeof Switch> = {
  title: 'Packages/UI Core/Forms/Switch',
  component: Switch,
  tags: ['autodocs'],
};

export default meta;

type Story = StoryObj<typeof Switch>;

const renderRow: Story['render'] = (args) => (
  <div className="flex items-center gap-3">
    <Switch id="notif" {...args} />
    <Label htmlFor="notif">Email notifications</Label>
  </div>
);

export const Default: Story = { render: renderRow };

export const On: Story = { args: { defaultChecked: true }, render: renderRow };

export const Disabled: Story = {
  args: { disabled: true, defaultChecked: true },
  render: renderRow,
};

function SettingsHost() {
  const [s, setS] = useState({ notifications: true, darkMode: false, autoSave: true });
  return (
    <div className="w-80 space-y-6">
      {(
        [
          ['notifications', 'Notifications', 'Receive push notifications'],
          ['darkMode', 'Dark Mode', 'Use dark theme'],
          ['autoSave', 'Auto Save', 'Save changes automatically'],
        ] as const
      ).map(([k, title, desc]) => (
        <div key={k} className="flex items-center justify-between">
          <div>
            <Label htmlFor={k} className="block">
              {title}
            </Label>
            <span className="text-sm text-muted-foreground">{desc}</span>
          </div>
          <Switch
            id={k}
            checked={s[k]}
            onCheckedChange={(c) => setS({ ...s, [k]: c })}
          />
        </div>
      ))}
    </div>
  );
}

export const Settings: Story = {
  render: () => <SettingsHost />,
};

/** Cloudflare-style notification cards — bordered rows with a pill toggle on the right. */
function CardsHost() {
  const [s, setS] = useState({ blog: false, education: true, events: false, product: true });
  const rows = [
    ['blog', 'Blog', 'Stay up to date on the trends from the technical visionaries building our next generation network.'],
    ['education', 'Education and Resources', 'Get the most from your subscription with helpful content and resources.'],
    ['events', 'Events', 'Receive the latest updates on upcoming in-person and online events, conferences, and webinars.'],
    ['product', 'Product News and Promotions', 'Learn about the latest products, features and promotions as soon as they launch.'],
  ] as const;
  return (
    <div className="w-[640px] space-y-4">
      {rows.map(([k, title, desc]) => (
        <div
          key={k}
          className="flex items-start justify-between gap-6 rounded-xl border border-border bg-card p-5"
        >
          <div>
            <Label htmlFor={k} className="block text-base font-semibold">
              {title}
            </Label>
            <span className="mt-1 block text-sm text-muted-foreground">{desc}</span>
          </div>
          <Switch
            id={k}
            checked={s[k]}
            onCheckedChange={(c) => setS({ ...s, [k]: c })}
          />
        </div>
      ))}
    </div>
  );
}

export const Cards: Story = {
  render: () => <CardsHost />,
};
