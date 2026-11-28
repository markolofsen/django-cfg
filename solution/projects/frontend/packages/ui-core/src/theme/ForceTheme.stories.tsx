import type { Meta, StoryObj } from '@storybook/react-vite';
import { Badge, Button, Card, CardContent, CardHeader, CardTitle } from '@djangocfg/ui-core/components';
import { ForceTheme } from '@djangocfg/ui-core/theme';

/**
 * `ForceTheme` regression showcase.
 *
 * `ForceTheme` re-declares the design tokens **inline** on a wrapper `<div>`.
 * Under the Tailwind v4 token contract the utilities read tokens RAW
 * (`.bg-muted { background-color: var(--muted) }`), so a token set to a bare HSL
 * triplet (`--muted: 0 0% 10%`) is an invalid color and the declaration is
 * silently dropped — producing **transparent fills + white-fallback borders**
 * inside the wrapped subtree. The token map is now wrapped in `hsl(...)`, which
 * closes that trap.
 *
 * This story is the visual proof. Every panel below leans on token-driven
 * utilities (`bg-card`, `bg-muted`, `border-border`, `bg-primary`, the status
 * tokens). If `ForceTheme` regresses to bare triplets, the `dark`/`light` panels
 * lose their fills and grow white borders while the "no ForceTheme" panel stays
 * correct — the bug is immediately obvious side-by-side.
 *
 * See `ui-core/src/theme/TROUBLESHOOTING.md`.
 */
const meta: Meta = {
  title: 'Packages/UI Core/Theme/ForceTheme',
  parameters: { layout: 'fullscreen' },
};
export default meta;

type Story = StoryObj;

/** A block of token-utility-sensitive UI. If tokens are valid, every surface has
 *  a visible fill and a hairline (not white) border. */
function TokenProbe({ label }: { label: string }) {
  return (
    <div className="space-y-4 p-6">
      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</p>

      {/* Surfaces — must all show a fill */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          ['bg-background', 'bg-background'],
          ['bg-card', 'bg-card'],
          ['bg-muted', 'bg-muted'],
          ['bg-accent', 'bg-accent'],
        ].map(([name, cls]) => (
          <div key={name} className={`flex h-16 items-center justify-center rounded-lg border border-border ${cls}`}>
            <code className="text-xs text-foreground">{name}</code>
          </div>
        ))}
      </div>

      {/* Borders — must be a hairline, NOT white */}
      <div className="flex flex-wrap gap-3">
        <div className="rounded-md border border-border px-3 py-2 text-sm text-foreground">border-border</div>
        <div className="rounded-md border border-divider px-3 py-2 text-sm text-foreground">border-divider</div>
        <div className="rounded-md border border-input bg-input px-3 py-2 text-sm text-foreground">input</div>
      </div>

      {/* Chat bubbles — the cmdop hero case: blue "You" + grey agent */}
      <div className="flex flex-col items-start gap-2">
        <span className="ml-auto rounded-2xl rounded-br-md bg-primary px-3 py-1.5 text-sm text-primary-foreground">
          Deploy to staging
        </span>
        <span className="rounded-2xl rounded-tl-md bg-muted px-3 py-1.5 text-sm text-foreground">
          On it — building from main.
        </span>
      </div>

      {/* Components + status */}
      <div className="flex flex-wrap items-center gap-3">
        <Button>Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="outline">Outline</Button>
        <Badge>Badge</Badge>
        <span className="rounded-full bg-success px-2 py-0.5 text-xs font-semibold text-on-success">12</span>
        <span className="rounded-md border border-warning-border bg-warning-background px-2 py-1 text-xs text-warning-foreground">
          warning
        </span>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Card surface</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Card body on <code>bg-card</code> with a <code>border-border</code> outline.
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * The three panels side-by-side: the page's own theme (no wrapper), then
 * `ForceTheme` dark, then `ForceTheme` light. All three must render identical
 * (correctly-filled) surfaces — only the palette differs.
 */
export const Regression: Story = {
  render: () => (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border p-6">
        <h1 className="text-lg font-semibold text-foreground">ForceTheme — token regression</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Every surface below must have a visible fill and a hairline (non-white) border in all three
          panels. Transparent fills or white borders inside the dark/light panels = the bare-triplet
          regression is back (see <code>theme/TROUBLESHOOTING.md</code>).
        </p>
      </div>

      <div className="grid gap-px bg-divider lg:grid-cols-3">
        {/* Panel 1: page theme, no ForceTheme — the control */}
        <div className="bg-background">
          <TokenProbe label="No ForceTheme (page theme)" />
        </div>

        {/* Panel 2: ForceTheme dark */}
        <ForceTheme theme="dark" className="bg-background">
          <TokenProbe label="ForceTheme · dark" />
        </ForceTheme>

        {/* Panel 3: ForceTheme light */}
        <ForceTheme theme="light" className="bg-background">
          <TokenProbe label="ForceTheme · light" />
        </ForceTheme>
      </div>
    </div>
  ),
};

/** ForceTheme dark alone, full width — the cmdop landing case. */
export const Dark: Story = {
  render: () => (
    <ForceTheme theme="dark" className="min-h-screen bg-background">
      <TokenProbe label="ForceTheme · dark (full width)" />
    </ForceTheme>
  ),
};

/** ForceTheme light alone, full width. */
export const Light: Story = {
  render: () => (
    <ForceTheme theme="light" className="min-h-screen bg-background">
      <TokenProbe label="ForceTheme · light (full width)" />
    </ForceTheme>
  ),
};
