import type { Meta, StoryObj } from '@storybook/react-vite';
import { GlowBackground } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Effects/GlowBackground',
  component: GlowBackground,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component:
          'Animated mesh-gradient backdrop. Renders `position: absolute inset-0` — must be placed inside a `position: relative` container. Content goes on top with `position: relative`.',
      },
    },
  },
} satisfies Meta<typeof GlowBackground>;

export default meta;

type Story = StoryObj<typeof meta>;

const stageStyle: React.CSSProperties = {
  position: 'relative',
  minHeight: 480,
  width: '100%',
  overflow: 'hidden',
  background: 'var(--background)',
};

export const Default: Story = {
  render: () => (
    <div style={stageStyle}>
      <GlowBackground />
      <div
        style={{
          position: 'relative',
          zIndex: 1,
          padding: '2rem',
          color: 'var(--muted-foreground)',
          fontSize: 14,
        }}
      >
        Default glow — uses theme <code>--primary</code> + indigo + purple blobs.
      </div>
    </div>
  ),
};

export const Tinted: Story = {
  parameters: {
    docs: {
      description: {
        story:
          'Tint via `className` — apply a CSS filter (hue-rotate / saturate) to recolor the entire glow without forking the component.',
      },
    },
  },
  render: () => (
    <div style={{ display: 'grid', gap: '1rem' }}>
      <div style={stageStyle}>
        <GlowBackground className="[filter:hue-rotate(120deg)_saturate(1.2)]" />
        <div
          style={{
            position: 'relative',
            zIndex: 1,
            padding: '2rem',
            color: 'var(--muted-foreground)',
            fontSize: 14,
          }}
        >
          Emerald tint — <code>hue-rotate(120deg)</code>
        </div>
      </div>
      <div style={stageStyle}>
        <GlowBackground className="[filter:hue-rotate(-40deg)_saturate(1.3)]" />
        <div
          style={{
            position: 'relative',
            zIndex: 1,
            padding: '2rem',
            color: 'var(--muted-foreground)',
            fontSize: 14,
          }}
        >
          Sunset tint — <code>hue-rotate(-40deg)</code>
        </div>
      </div>
      <div style={stageStyle}>
        <GlowBackground className="[filter:grayscale(1)_brightness(0.9)]" />
        <div
          style={{
            position: 'relative',
            zIndex: 1,
            padding: '2rem',
            color: 'var(--muted-foreground)',
            fontSize: 14,
          }}
        >
          Mono tint — <code>grayscale(1)</code>
        </div>
      </div>
    </div>
  ),
};

export const WithContent: Story = {
  parameters: {
    docs: {
      description: {
        story: 'Hero composition — glow as backdrop, headline + CTA layered on top.',
      },
    },
  },
  render: () => (
    <div style={{ ...stageStyle, minHeight: 600 }}>
      <GlowBackground />
      <div
        style={{
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: 600,
          padding: '2rem',
          textAlign: 'center',
        }}
      >
        <h1
          style={{
            fontSize: 56,
            fontWeight: 700,
            lineHeight: 1.1,
            margin: 0,
            color: 'var(--foreground)',
            letterSpacing: '-0.03em',
          }}
        >
          Ship faster.
          <br />
          Glow harder.
        </h1>
        <p
          style={{
            marginTop: '1rem',
            maxWidth: 520,
            fontSize: 18,
            color: 'var(--muted-foreground)',
          }}
        >
          A drop-in animated backdrop for landing pages, marketing hero sections, and empty states.
        </p>
        <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.75rem' }}>
          <button
            type="button"
            style={{
              padding: '0.625rem 1.25rem',
              borderRadius: 8,
              background: 'var(--primary)',
              color: 'var(--primary-foreground)',
              fontWeight: 600,
              border: 'none',
              cursor: 'pointer',
            }}
          >
            Get started
          </button>
          <button
            type="button"
            style={{
              padding: '0.625rem 1.25rem',
              borderRadius: 8,
              background: 'transparent',
              color: 'var(--foreground)',
              fontWeight: 600,
              border: '1px solid var(--border)',
              cursor: 'pointer',
            }}
          >
            Learn more
          </button>
        </div>
      </div>
    </div>
  ),
};
