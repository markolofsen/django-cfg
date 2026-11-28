import type { Meta, StoryObj } from '@storybook/react-vite';
import { Sparkles } from 'lucide-react';

import { AuthShell } from '@djangocfg/layouts';
import {
  Button,
  Input,
  Label,
} from '@djangocfg/ui-core/components';

/**
 * `AuthShell` — the chrome of `AuthLayout` without the OTP/OAuth state
 * machine. Lets us preview the shell variants without wiring auth APIs.
 */

// A landscape photo so the split variant's frosted-glass card has something
// to blur over. Unsplash "source" — stable, no key needed.
const BG_IMAGE =
  'https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=2000&q=80';

function MockForm({
  title,
  /** Centered has no sidebar, so it carries the brand; split hides it. */
  showBrand = true,
}: {
  title: string;
  showBrand?: boolean;
}) {
  return (
    <form
      className="grid w-full max-w-sm gap-5"
      onSubmit={(e) => {
        e.preventDefault();
      }}
    >
      <header className="grid gap-1.5">
        {showBrand && (
          <span className="inline-flex items-center gap-2 text-base font-semibold">
            <Sparkles className="h-5 w-5 text-primary" /> djangocfg
          </span>
        )}
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        <p className="text-sm text-muted-foreground">
          Enter your email to continue.
        </p>
      </header>
      <div className="grid gap-1.5">
        <Label htmlFor="email">Email</Label>
        <Input id="email" type="email" placeholder="you@example.com" autoComplete="email" />
      </div>
      <Button type="submit" className="w-full">
        Continue
      </Button>
      <p className="text-center text-xs text-muted-foreground">
        By continuing you agree to the Terms and Privacy Policy.
      </p>
    </form>
  );
}

function SidebarBranding() {
  return (
    <div className="flex h-full flex-col justify-between">
      <span className="inline-flex items-center gap-2 text-base font-semibold text-foreground">
        <Sparkles className="h-5 w-5 text-primary" /> djangocfg
      </span>
      <blockquote className="space-y-3">
        <p className="text-lg leading-snug text-foreground">
          “Set up auth, profile and billing in an afternoon — not a sprint.”
        </p>
        <footer className="text-sm text-muted-foreground">
          — A djangocfg developer
        </footer>
      </blockquote>
    </div>
  );
}

const meta = {
  title: 'Packages/Layouts/AuthShell',
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component:
          '`AuthShell` chrome in two variants — `centered` (Apple-style, glow background) and `split` (frosted-glass card over a background image on desktop; a plain centered form on mobile).',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Centered: Story = {
  render: () => (
    <div className="h-[760px]">
      <AuthShell variant="centered">
        <MockForm title="Sign in" />
      </AuthShell>
    </div>
  ),
};

export const Split: Story = {
  render: () => (
    <div className="h-[760px]">
      <AuthShell
        variant="split"
        background={{ imageUrl: BG_IMAGE }}
        sidebar={<SidebarBranding />}
      >
        <MockForm title="Welcome back" showBrand={false} />
      </AuthShell>
    </div>
  ),
};
