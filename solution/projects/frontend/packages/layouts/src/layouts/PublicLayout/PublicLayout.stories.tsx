import type { Meta, StoryObj } from '@storybook/react-vite';
import { Sparkles } from 'lucide-react';

import {
  FloatingNavbar,
  FlushNavbar,
  PublicLayout,
} from '@djangocfg/layouts';
import { MockAuthProvider, buildMockUser } from '@djangocfg/layouts/testing';
import { ThemeProvider } from '@djangocfg/ui-core/theme';

/**
 * Local theme provider — pages with chrome (footer, theme switcher) read
 * `useThemeContext`. The global preview decorator deliberately omits it
 * to avoid racing with `addon-themes`. Story-scoped is safe.
 */
function Frame({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider defaultTheme="dark">
      <div className="h-[760px] w-[1100px] overflow-auto rounded-lg border border-border bg-background">
        {children}
      </div>
    </ThemeProvider>
  );
}

const navigation = [
  { label: 'Home', href: '/' },
  { label: 'Docs', href: '/docs' },
  { label: 'Pricing', href: '/pricing' },
  { label: 'Blog', href: '/blog' },
];

// Navigation with a dropdown group — used to verify the desktop dropdown panel
// shares the navbar's translucent glass (bg-background/72 + blur), not a flat
// near-opaque surface.
const navigationWithDropdown = [
  {
    label: 'Products',
    href: '/products',
    items: [
      { label: 'SDK', href: '/sdk' },
      { label: 'Connect', href: '/connect' },
      { label: 'Bots', href: '/bots' },
      { label: 'Server', href: '/server' },
    ],
  },
  { label: 'Docs', href: '/docs' },
  { label: 'Pricing', href: '/pricing' },
  { label: 'Blog', href: '/blog' },
];

function Brand() {
  return (
    <span className="inline-flex items-center gap-2 text-base font-semibold">
      <Sparkles className="h-5 w-5 text-primary" /> djangocfg
    </span>
  );
}

function PageBody({
  title,
  body,
}: {
  title: string;
  body: string;
}) {
  return (
    <section className="mx-auto max-w-7xl px-4 py-12">
      <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
      <p className="mt-2 max-w-2xl text-muted-foreground">{body}</p>
      <div className="mt-8 grid grid-cols-1 gap-4 md:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-lg border border-border bg-card p-4 text-card-foreground"
          >
            <div className="text-sm font-medium">Card {i}</div>
            <p className="mt-1 text-sm text-muted-foreground">
              Placeholder content to fill the layout.
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

const meta = {
  title: 'Packages/Layouts/PublicLayout',
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          '`PublicLayout` shell with two navbar variants. Footer slot is intentionally left empty here — the real `DefaultFooter` pulls in `useThemeContext`, locale switcher and other plumbing that belongs in a fuller "BaseApp" story. Migrated from `apps/demo/(playground)/ui/layouts/public/`.',
      },
    },
    nextjs: { appDirectory: true },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Floating: Story = {
  render: () => (
    <Frame>
      <PublicLayout
        navbar={
          <FloatingNavbar
            config={{
              brand: <Brand />,
              navigation,
              shell: { className: 'mx-auto max-w-7xl' },
            }}
          />
        }
      >
        <PageBody
          title="Floating navbar variant"
          body="The navbar floats above the content with a rounded translucent surface. Resize the canvas to see the mobile drawer kick in."
        />
      </PublicLayout>
    </Frame>
  ),
};

export const Flush: Story = {
  render: () => (
    <Frame>
      <PublicLayout
        navbar={
          <FlushNavbar
            config={{
              brand: <Brand />,
              navigation,
              shell: { className: 'mx-auto max-w-7xl' },
            }}
          />
        }
      >
        <PageBody
          title="Flush navbar variant"
          body="Edge-to-edge navbar with a hairline bottom border. Better for content-dense apps."
        />
      </PublicLayout>
    </Frame>
  ),
};

/**
 * Dropdown glass — hover/click **Products** to confirm the desktop dropdown
 * panel uses the SAME translucent glass surface as the navbar (bg-background/72
 * + 10px blur), so page content shows frosted through it. Previously the panel
 * was near-opaque (bg-background/95 + blur-sm) and read flat next to the bar.
 */
export const DropdownGlass: Story = {
  render: () => (
    <Frame>
      <PublicLayout
        navbar={
          <FloatingNavbar
            config={{
              brand: <Brand />,
              navigation: navigationWithDropdown,
              shell: { className: 'mx-auto max-w-7xl' },
            }}
          />
        }
      >
        <PageBody
          title="Dropdown glass"
          body="Hover “Products”: the dropdown frosts the content behind it like the navbar does."
        />
      </PublicLayout>
    </Frame>
  ),
};

/**
 * Signed in: the shared account menu (the same one the private shell uses) in the navbar's top right. Click the
 * avatar on desktop; narrow the canvas and open the drawer for the inline variant.
 */
export const SignedIn: Story = {
  render: () => (
    <MockAuthProvider user={buildMockUser()}>
      <Frame>
        <PublicLayout
          navbar={
            <FloatingNavbar
              config={{
                brand: <Brand />,
                navigation,
                shell: { className: 'mx-auto max-w-7xl' },
                userMenu: { groups: [{ items: [{ label: 'Billing', href: '/billing' }, { label: 'Team', href: '/team' }] }] },
              }}
            />
          }
        >
          <PageBody title="Signed-in navbar" body="The avatar opens the shared account menu: Settings, your groups, Sign out." />
        </PublicLayout>
      </Frame>
    </MockAuthProvider>
  ),
};
