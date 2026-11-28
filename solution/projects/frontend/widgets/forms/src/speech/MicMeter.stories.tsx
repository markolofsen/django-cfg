import { useEffect, useRef, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';

import { MicMeter } from '.';

type Args = {
  bars: number;
  gap: number;
  barWidth: number;
  height: number;
  source: 'synthetic-sine' | 'synthetic-noise' | 'static';
  staticLevel: number;
};

function useSyntheticLevel(
  source: Args['source'],
  staticLevel: number,
): number {
  const [level, setLevel] = useState(0);
  const tRef = useRef(0);
  useEffect(() => {
    if (source === 'static') {
      setLevel(staticLevel);
      return undefined;
    }
    tRef.current = 0;
    const id = window.setInterval(() => {
      tRef.current += 0.12;
      if (source === 'synthetic-sine') {
        setLevel((Math.sin(tRef.current) + 1) / 2);
      } else {
        // Bursty pseudo-noise — feels like real speech.
        const burst = Math.random() < 0.85 ? Math.random() * 0.7 : Math.random();
        setLevel(burst);
      }
    }, 90);
    return () => window.clearInterval(id);
  }, [source, staticLevel]);
  return level;
}

function MicMeterDemo({
  bars,
  gap,
  barWidth,
  height,
  source,
  staticLevel,
}: Args) {
  const level = useSyntheticLevel(source, staticLevel);
  return (
    <div className="flex w-[360px] flex-col gap-3 rounded-lg border border-border bg-background p-4">
      <div className="flex items-center gap-3">
        <MicMeter
          level={level}
          bars={bars}
          gap={gap}
          barWidth={barWidth}
          height={height}
        />
        <span className="font-mono text-xs text-muted-foreground">
          level: {level.toFixed(2)}
        </span>
      </div>
      <p className="text-xs text-muted-foreground">
        The bar values come from a synthetic generator here so you can see
        the animation without granting mic access. In production wire the
        meter to <code className="font-mono">useMicLevel(stream)</code>
        where <code className="font-mono">stream</code> is the
        <code className="font-mono"> MediaStream</code> from
        <code className="font-mono"> engine.getStream?.()</code>.
      </p>
    </div>
  );
}

const meta = {
  title: 'Widgets/Forms/Speech/Mic meter',
  component: MicMeterDemo,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          '`MicMeter` is a dependency-free RMS bar meter. Pair it with `useMicLevel(stream)` to show actual mic level.',
      },
    },
  },
  argTypes: {
    bars: {
      control: { type: 'number', min: 4, max: 32, step: 1 },
      table: { category: 'Meter' },
    },
    gap: {
      control: { type: 'number', min: 0, max: 8 },
      table: { category: 'Meter' },
    },
    barWidth: {
      control: { type: 'number', min: 1, max: 10 },
      table: { category: 'Meter' },
    },
    height: {
      control: { type: 'number', min: 12, max: 64 },
      table: { category: 'Meter' },
    },
    source: {
      control: 'inline-radio',
      options: ['synthetic-sine', 'synthetic-noise', 'static'],
      table: { category: 'Signal' },
    },
    staticLevel: {
      control: { type: 'range', min: 0, max: 1, step: 0.05 },
      if: { arg: 'source', eq: 'static' },
      table: { category: 'Signal' },
    },
  },
  args: {
    bars: 16,
    gap: 2,
    barWidth: 3,
    height: 32,
    source: 'synthetic-sine',
    staticLevel: 0.4,
  },
} satisfies Meta<typeof MicMeterDemo>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Playground: Story = {};

export const Animated: Story = { args: { source: 'synthetic-sine' } };

export const NoiseBursts: Story = { args: { source: 'synthetic-noise' } };

export const Static: Story = { args: { source: 'static', staticLevel: 0.6 } };
