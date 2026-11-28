import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/Tabs',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const SimpleTabs: Story = {
  render: () => (
    <Tabs defaultValue="tab1" className="w-[420px]">
      <TabsList>
        <TabsTrigger value="tab1">Tab 1</TabsTrigger>
        <TabsTrigger value="tab2">Tab 2</TabsTrigger>
        <TabsTrigger value="tab3">Tab 3</TabsTrigger>
      </TabsList>
      <TabsContent value="tab1" className="p-4">Content for Tab 1</TabsContent>
      <TabsContent value="tab2" className="p-4">Content for Tab 2</TabsContent>
      <TabsContent value="tab3" className="p-4">Content for Tab 3</TabsContent>
    </Tabs>
  ),
};

export const DisabledTab: Story = {
  render: () => (
    <Tabs defaultValue="active" className="w-[420px]">
      <TabsList>
        <TabsTrigger value="active">Active</TabsTrigger>
        <TabsTrigger value="disabled" disabled>
          Disabled
        </TabsTrigger>
        <TabsTrigger value="another">Another</TabsTrigger>
      </TabsList>
      <TabsContent value="active" className="p-4">
        This tab is active.
      </TabsContent>
      <TabsContent value="another" className="p-4">
        Another active tab.
      </TabsContent>
    </Tabs>
  ),
};

export const Default: Story = {
  render: () => (
    <Tabs defaultValue="account" className="w-[400px]">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="account">Account</TabsTrigger>
        <TabsTrigger value="billing">Billing</TabsTrigger>
        <TabsTrigger value="team">Team</TabsTrigger>
      </TabsList>
      <TabsContent
        value="account"
        className="rounded-md border border-border p-4 text-sm"
      >
        Account preferences live here.
      </TabsContent>
      <TabsContent
        value="billing"
        className="rounded-md border border-border p-4 text-sm"
      >
        Payment methods and invoices.
      </TabsContent>
      <TabsContent
        value="team"
        className="rounded-md border border-border p-4 text-sm"
      >
        Invite teammates and manage roles.
      </TabsContent>
    </Tabs>
  ),
};

/* ---------------------------------------------------------------------------
 * Variants and sizing
 * ------------------------------------------------------------------------ */

/** The catalogue's own vocabulary — labels of visibly different widths, which
 *  is what a real segmented control has to survive. */
const MODES = ['All', 'Deals', 'New', 'Used'];

/**
 * The capsule. Its indicator TRAVELS to the selected tab rather than appearing
 * on it — one object moving between options is what says they are mutually
 * exclusive.
 *
 * The pill is measured from the active trigger, so tabs of different widths
 * ("All" against "Body type") each get an indicator of their own width. A
 * reader with reduced-motion gets the destination without the journey.
 */
export const Pill: Story = {
  render: () => (
    <Tabs defaultValue="All">
      <TabsList variant="pill">
        {MODES.map((mode) => (
          <TabsTrigger key={mode} value={mode}>
            {mode}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  ),
};

/** `md` (36px) beside `sm` (28px). `size="auto"` picks between them at the
 *  mobile breakpoint, which is the prop a toolbar usually wants. */
export const Sizes: Story = {
  render: () => (
    <div className="flex flex-col items-start gap-6">
      {(['md', 'sm'] as const).map((size) => (
        <div key={size} className="flex flex-col gap-1.5">
          <span className="text-xs text-muted-foreground">size={`"${size}"`}</span>
          <Tabs defaultValue="All">
            <TabsList variant="pill" size={size}>
              {MODES.map((mode) => (
                <TabsTrigger key={mode} value={mode}>
                  {mode}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        </div>
      ))}
    </div>
  ),
};

/**
 * `fullWidth="mobile"`: hugs its labels on a desktop row, where the switch
 * sits beside other controls, and spans the width on a phone, where it is
 * alone. Both consumers of this component were writing that as `fullWidth`
 * plus a CSS media query undoing it.
 *
 * Resize the frame across 768px to see it change.
 */
export const FullWidthOnMobile: Story = {
  render: () => (
    <Tabs defaultValue="All" className="w-full">
      <TabsList variant="pill" fullWidth="mobile" size="auto">
        {MODES.map((mode) => (
          <TabsTrigger key={mode} value={mode} flexEqual>
            {mode}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  ),
};

/** All three variants together, for comparing weight and density. */
export const Variants: Story = {
  render: () => (
    <div className="flex flex-col items-start gap-6">
      {(['pill', 'default', 'underline'] as const).map((variant) => (
        <div key={variant} className="flex flex-col gap-1.5">
          <span className="text-xs text-muted-foreground">variant={`"${variant}"`}</span>
          <Tabs defaultValue="All">
            <TabsList variant={variant}>
              {MODES.map((mode) => (
                <TabsTrigger key={mode} value={mode}>
                  {mode}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        </div>
      ))}
    </div>
  ),
};
