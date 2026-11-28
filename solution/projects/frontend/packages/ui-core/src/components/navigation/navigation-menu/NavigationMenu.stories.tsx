import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/NavigationMenu',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

const sections = [
  {
    title: 'Getting started',
    items: [
      { title: 'Installation', href: '/docs/install', desc: 'Install via npm or pnpm.' },
      { title: 'Quickstart', href: '/docs/quickstart', desc: 'Build your first page.' },
    ],
  },
  {
    title: 'Components',
    items: [
      { title: 'Forms', href: '/docs/forms', desc: 'Inputs, selects, validation.' },
      { title: 'Overlay', href: '/docs/overlay', desc: 'Dialog, sheet, popover.' },
      { title: 'Navigation', href: '/docs/navigation', desc: 'Menubar, sidebar, links.' },
    ],
  },
  {
    title: 'Resources',
    items: [
      { title: 'Changelog', href: '/changelog', desc: "What's new." },
      { title: 'GitHub', href: 'https://github.com', desc: 'Source on GitHub.' },
    ],
  },
];

export const Default: Story = {
  render: () => (
    <NavigationMenu>
      <NavigationMenuList>
        {sections.map((section) => (
          <NavigationMenuItem key={section.title}>
            <NavigationMenuTrigger>{section.title}</NavigationMenuTrigger>
            <NavigationMenuContent>
              <ul className="grid w-[400px] gap-2 p-3 md:w-[500px] md:grid-cols-2">
                {section.items.map((item) => (
                  <li key={item.title}>
                    <NavigationMenuLink href={item.href}>
                      <div className="rounded-md p-3 hover:bg-accent">
                        <div className="text-sm font-medium">{item.title}</div>
                        <div className="text-xs text-muted-foreground">{item.desc}</div>
                      </div>
                    </NavigationMenuLink>
                  </li>
                ))}
              </ul>
            </NavigationMenuContent>
          </NavigationMenuItem>
        ))}
      </NavigationMenuList>
    </NavigationMenu>
  ),
};

export const WithLinks: Story = {
  render: () => (
    <NavigationMenu>
      <NavigationMenuList>
        <NavigationMenuItem>
          <NavigationMenuLink href="/" className={navigationMenuTriggerStyle()}>
            Home
          </NavigationMenuLink>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuLink href="/docs" className={navigationMenuTriggerStyle()}>
            Docs
          </NavigationMenuLink>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuLink href="/pricing" className={navigationMenuTriggerStyle()}>
            Pricing
          </NavigationMenuLink>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuLink href="https://github.com" className={navigationMenuTriggerStyle()}>
            GitHub
          </NavigationMenuLink>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  ),
};
