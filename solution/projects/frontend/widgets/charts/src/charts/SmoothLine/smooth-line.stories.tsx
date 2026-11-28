import * as React from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  SmoothLine,
  type SmoothLineColor,
} from '.';
import { Sparkline } from '../Sparkline';

const COLORS: SmoothLineColor[] = [
  'primary',
  'success',
  'warning',
  'destructive',
  'info',
  'currentColor',
];

const SAMPLE = [
  12, 14, 11, 18, 22, 19, 24, 28, 26, 31, 35, 33, 38, 42, 40, 46, 49, 52, 50, 58,
];

const meta = {
  title: 'Widgets/Charts/SmoothLine',
  component: SmoothLine,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Streaming sibling of `Sparkline`, drawn on a CANVAS. (1) Curve smoothness — the line is a MONOTONE-CUBIC curve (Fritsch–Carlson / d3 `curveMonotoneX`) through the points, so it flows in gentle curves WITHOUT overshooting or inventing values between data points; `tension={0}` degenerates to straight segments. (2) Streaming smoothness — `scroll` runs a single wall-clock rAF loop that, every frame, `clearRect`s the canvas and redraws the WHOLE line at its scrolled X. One writer, one clock — so the SVG-era jump-then-catch-up (path rebuilt on one clock, transform animated on another) is impossible by construction. A one-interval `delay` holds the right edge back so the newest point slides in cleanly (clipped for free by `clearRect`). Crisp on retina via `devicePixelRatio` scaling. Honours `prefers-reduced-motion` (static single draw; curve SHAPE stays curved) and pauses on a hidden tab.',
      },
    },
  },
  argTypes: {
    color: { control: 'select', options: COLORS },
    width: { control: { type: 'number', min: 40, max: 480 } },
    height: { control: { type: 'number', min: 16, max: 160 } },
    strokeWidth: { control: { type: 'number', min: 0.5, max: 4, step: 0.25 } },
    tweenMs: { control: { type: 'number', min: 0, max: 4000, step: 100 } },
    tension: { control: { type: 'number', min: 0, max: 1, step: 0.05 } },
    area: { control: 'boolean' },
    scroll: { control: 'boolean' },
    delay: { control: 'boolean' },
  },
} satisfies Meta<typeof SmoothLine>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { values: SAMPLE, color: 'info', area: true, height: 48 },
};

export const Area: Story = {
  args: { values: SAMPLE, color: 'success', area: true, height: 56 },
};

/**
 * Curve smoothness proof — the SAME data drawn two ways. The bottom row
 * (`tension={0}`) is the OLD straight-segment sparkline look: sharp angles at
 * every point. The top (`tension={0.5}`, the default) is the MONOTONE curve —
 * it flows in gentle curves but, unlike Catmull-Rom, never overshoots a local
 * max/min or invents a value the data never had. Pure geometry, no animation.
 */
export const CurvedVsStraight: Story = {
  args: { values: SAMPLE },
  render: () => {
    const rows: { label: string; tension: number }[] = [
      { label: 'tension 0.5 — DEFAULT monotone-cubic curve (no overshoot)', tension: 0.5 },
      { label: 'tension 0 — straight segments (old sparkline / disable path)', tension: 0 },
    ];
    return (
      <div className="flex w-[440px] flex-col gap-4">
        {rows.map((r) => (
          <div key={r.tension} className="flex flex-col gap-1">
            <span className="text-xs font-medium text-muted-foreground">
              {r.label}
            </span>
            <div className="rounded-md border border-border bg-card/40 p-2">
              <SmoothLine
                values={SAMPLE}
                color={r.tension === 0 ? 'destructive' : 'info'}
                area
                width={420}
                height={64}
                tension={r.tension}
              />
            </div>
          </div>
        ))}
        <p className="text-[11px] text-muted-foreground">
          Same data, two curves. The bottom (sharp, red) is the previous
          straight-segment look; the default 0.5 (top) is a flowing monotone
          curve that stays within the data&apos;s own bounds — it cannot wobble or
          overshoot between points.
        </p>
      </div>
    );
  },
};

/**
 * Token bridge — `color="currentColor"` inherits the ancestor `text-*` tint
 * (here a Tailwind `text-emerald-500` class). The canvas reads the resolved CSS
 * `color` off itself (`getComputedStyle(canvas).color`) and passes it to
 * `ctx.strokeStyle` — re-resolved on theme change. This is how cmdop keeps its
 * `text-chart-*` tinting on the shared primitive.
 */
export const CurrentColorBridge: Story = {
  args: { values: SAMPLE, color: 'currentColor', area: true, height: 48 },
  render: (args) => (
    <span className="text-chart-1">
      <SmoothLine {...args} />
    </span>
  ),
};

/**
 * THE STREAMING PROOF. A 1 Hz synthetic feed drives a scrolling SmoothLine
 * (top) and a static Sparkline (bottom) with the SAME values. The SmoothLine
 * slides left at constant velocity — a continuous monotone curve flowing past,
 * no per-second lurch, no vertical rubber-band. The Sparkline (bottom) JUMPS a
 * whole frame each second.
 *
 * `jitterMs` makes the feed UNEVEN (real data is not a metronome — the Go stats
 * ticker + the Wails event bus add ±100-200ms). The whole point of the engine is
 * that the scroll velocity stays STEADY even when arrivals jitter: it MEASURES
 * the cadence (EMA) and never freezes-then-snaps on a late sample. A perfectly
 * even feed hides that bug — the jittery feed is the real test.
 */
function LiveStream({
  tweenMs,
  scroll,
  jitterMs = 0,
}: {
  tweenMs: number;
  scroll: boolean;
  jitterMs?: number;
}) {
  const [values, setValues] = React.useState<number[]>(() =>
    Array.from({ length: 24 }, (_, i) => 30 + Math.sin(i / 3) * 18),
  );

  React.useEffect(() => {
    let id: ReturnType<typeof setTimeout>;
    const schedule = () => {
      const gap = tweenMs + (Math.random() * 2 - 1) * jitterMs;
      id = setTimeout(() => {
        setValues((prev) => {
          const next = prev.slice(1);
          const last = prev[prev.length - 1] ?? 0;
          const v = Math.max(
            2,
            Math.min(100, last + (Math.random() - 0.5) * 36),
          );
          next.push(v);
          return next;
        });
        schedule();
      }, Math.max(50, gap));
    };
    schedule();
    return () => clearTimeout(id);
  }, [tweenMs, jitterMs]);

  return (
    <div className="flex w-[420px] flex-col gap-4">
      <div className="flex flex-col gap-1">
        <span className="text-xs font-medium text-muted-foreground">
          SmoothLine — canvas constant-velocity scroll (slot {tweenMs}ms
          {jitterMs ? ` ±${jitterMs}ms jitter` : ''}
          {scroll ? ', scroll' : ', no scroll'})
        </span>
        <div className="rounded-md border border-border bg-card/40 p-2">
          <SmoothLine
            values={values}
            color="info"
            area
            height={56}
            tweenMs={tweenMs}
            scroll={scroll}
          />
        </div>
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-xs font-medium text-muted-foreground">
          Sparkline — jumps (static, instant `d` swap)
        </span>
        <div className="rounded-md border border-border bg-card/40 p-2">
          <Sparkline
            data={values}
            variant="area"
            color="primary"
            width={400}
            height={56}
            showEndpoint={false}
          />
        </div>
      </div>
      <p className="text-[11px] text-muted-foreground">
        Same 1 Hz data source. The top line should FLOW left at a perfectly
        constant speed (no per-second lurch, no vertical rubber-band). Toggle{' '}
        <code>prefers-reduced-motion: reduce</code> in your OS / devtools — the
        top line then renders static (a11y fallback). Background the tab and the
        scroll pauses.
      </p>
    </div>
  );
}

export const LiveStreamScroll: Story = {
  args: { values: SAMPLE, tweenMs: 1000, scroll: true },
  render: (args) => (
    <LiveStream tweenMs={args.tweenMs ?? 1000} scroll={args.scroll ?? true} />
  ),
};

/**
 * THE REAL TEST — a JITTERY 1 Hz feed (1000ms ±200ms). A perfectly even feed
 * hides the freeze-then-snap; uneven arrivals expose it. The engine MEASURES the
 * cadence (EMA of arrival deltas) and drives the scroll off that, so the trace
 * must STILL glide at a steady velocity with NO per-tick freeze or snap.
 *
 * The read-out below SAMPLES the rightmost canvas pixels every frame: it finds
 * the X of the right-most stroked (non-blank) column. On the canvas engine that
 * edge must advance SMOOTHLY (small steady dx/frame, then a one-slot reseat at
 * each commit as the next point scrolls in) — NEVER a jump-then-slow-catch-up.
 * Because the whole line is redrawn every frame at one wall-clock X, the
 * two-writer desync that produced that artifact cannot occur here.
 */
function JitteryStream() {
  const rootRef = React.useRef<HTMLDivElement | null>(null);
  const [stats, setStats] = React.useState({
    edge: 0,
    dEdge: 0,
    cov: 0,
    meanV: 0,
    n: 0,
  });
  const prevEdgeRef = React.useRef(0);
  // Rolling window of per-frame velocities (px/frame) during steady glide. We
  // EXCLUDE commit-seam frames (the one-slot reseat as the next point scrolls in
  // shows as a big negative step) so the window measures the VISIBLE scroll speed
  // only — the thing that must be rock-steady. The coefficient of variation
  // (stddev / mean) of that window is the residual-jitter metric: ~0 = perfect.
  const velWindowRef = React.useRef<number[]>([]);

  React.useEffect(() => {
    let raf = 0;
    const sample = () => {
      raf = requestAnimationFrame(sample);
      const canvas = rootRef.current?.querySelector('canvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      const w = canvas.width;
      const h = canvas.height;
      // Scan right→left for the first column that has any stroked pixel — the
      // current right edge of the trace, in device px.
      let edge = 0;
      try {
        const img = ctx.getImageData(0, 0, w, h).data;
        outer: for (let x = w - 1; x >= 0; x -= 1) {
          for (let y = 0; y < h; y += 1) {
            if (img[(y * w + x) * 4 + 3] !== 0) {
              edge = x;
              break outer;
            }
          }
        }
      } catch {
        return; // tainted canvas etc. — skip
      }
      const dEdge = edge - prevEdgeRef.current;
      prevEdgeRef.current = edge;

      // Collect steady-glide velocities only. The edge advances right (dEdge > 0)
      // during the slide; the commit reseat is a sharp negative step. Keep small
      // positive deltas (the constant-velocity glide); drop the reseat + the
      // first frame (dEdge huge from the 0 seed). Window = last 80 frames.
      if (dEdge > 0 && dEdge < w * 0.25) {
        const win = velWindowRef.current;
        win.push(dEdge);
        if (win.length > 80) win.shift();
        const n = win.length;
        const mean = win.reduce((a, b) => a + b, 0) / n;
        const variance =
          win.reduce((a, b) => a + (b - mean) * (b - mean), 0) / n;
        const cov = mean > 0 ? Math.sqrt(variance) / mean : 0;
        setStats({ edge, dEdge, cov, meanV: mean, n });
      } else {
        setStats((s) => ({ ...s, edge, dEdge }));
      }
    };
    raf = requestAnimationFrame(sample);
    return () => cancelAnimationFrame(raf);
  }, []);

  const covPct = (stats.cov * 100).toFixed(1);
  const steady = stats.n >= 30 && stats.cov < 0.05;

  return (
    <div className="flex w-[440px] flex-col gap-2" ref={rootRef}>
      <LiveStream tweenMs={1000} scroll jitterMs={200} />
      <div className="rounded-md border border-border bg-card/40 p-2 font-mono text-[11px] tabular-nums text-muted-foreground">
        rightEdge={stats.edge}px · dEdge/frame={stats.dEdge}px
        <div className="mt-1">
          glide velocity: mean={stats.meanV.toFixed(2)}px/frame · CoV={covPct}%
          {' '}(n={stats.n})
          {stats.n >= 30 && (
            <span className={steady ? 'text-success' : 'text-destructive'}>
              {' '}
              {steady ? '✓ STEADY (CoV≈0)' : '✗ wobble'}
            </span>
          )}
        </div>
        <div className="mt-1 text-[10px]">
          The glide velocity (per-frame edge advance, commit reseats excluded) must
          be a near-constant ramp on this jittery feed — CoV (stddev/mean) should
          fall toward ~0 as the window fills. Before the residual-jitter fix the
          velocity micro-adjusted every commit (measurable CoV); the slewed/decoupled
          velocity flattens it.
        </div>
      </div>
    </div>
  );
}

export const JitteryFeed: Story = {
  args: { values: SAMPLE, tweenMs: 1000, scroll: true },
  render: () => <JitteryStream />,
};

/**
 * SMOOTH vs JAGGED, side by side, on the SAME 1 Hz feed. LEFT is the canvas
 * model (`scroll` on): a constant-velocity slide with a monotone curve — buttery.
 * RIGHT is the static instant-swap (`scroll` off): every second the whole frame
 * teleports — the jagged look the rewrite removes.
 */
function SmoothVsJagged() {
  const [values, setValues] = React.useState<number[]>(() =>
    Array.from({ length: 24 }, (_, i) => 40 + Math.sin(i / 2.5) * 22),
  );

  React.useEffect(() => {
    const id = setInterval(() => {
      setValues((prev) => {
        const next = prev.slice(1);
        const last = prev[prev.length - 1] ?? 0;
        const v = Math.max(2, Math.min(100, last + (Math.random() - 0.5) * 40));
        next.push(v);
        return next;
      });
    }, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex w-[680px] gap-4">
      <div className="flex flex-1 flex-col gap-1">
        <span className="text-xs font-medium text-success">
          NEW — canvas constant-velocity scroll + monotone curve (smooth)
        </span>
        <div className="rounded-md border border-border bg-card/40 p-2">
          <SmoothLine values={values} color="success" area height={64} scroll tweenMs={1000} />
        </div>
      </div>
      <div className="flex flex-1 flex-col gap-1">
        <span className="text-xs font-medium text-destructive">
          OLD — instant swap each tick (jagged teleport)
        </span>
        <div className="rounded-md border border-border bg-card/40 p-2">
          <SmoothLine values={values} color="destructive" area height={64} scroll={false} tweenMs={0} />
        </div>
      </div>
    </div>
  );
}

export const SmoothVsJaggedCompare: Story = {
  args: { values: SAMPLE },
  render: () => <SmoothVsJagged />,
};

export const Colors: Story = {
  args: { values: SAMPLE },
  render: () => (
    <div className="flex flex-wrap items-center gap-6">
      {COLORS.filter((c) => c !== 'currentColor').map((color) => (
        <div key={color} className="flex flex-col items-center gap-1">
          <div className="w-[160px]">
            <SmoothLine values={SAMPLE} color={color} area width={160} />
          </div>
          <span className="text-xs text-muted-foreground">{color}</span>
        </div>
      ))}
    </div>
  ),
};

export const Empty: Story = {
  args: { values: [] },
};
