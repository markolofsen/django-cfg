# SmoothLine

Animated sibling of [`Sparkline`](../Sparkline/README.md). Same pure-SVG family
(fixed viewBox, `preserveAspectRatio="none"`, `vectorEffect="non-scaling-stroke"`),
but with **two** kinds of smoothness:

1. **Curve smoothness (the line SHAPE).** The line is drawn as a flowing
   **Catmull-Rom → cubic-bezier curve** through the points (`M … C …`), not a
   jagged `M … L …` polyline — so it flows in gentle curves instead of kinking
   at each data point. Controlled by `tension` (default `0.5`; `0` degenerates
   to straight `L` segments — the disable path for charts that want SHARP
   geometry like an ECG QRS spike). This is pure geometry: the curve is rebuilt
   from the points each frame, so it both flows AND glides.
2. **Streaming smoothness (the MOTION).** With `scroll` on, the trace slides
   left at **constant velocity** like a hospital monitor (the professional
   D3/Smoothie model) instead of snapping the `d` each tick. We animate exactly
   ONE thing — a `translateX` on the scroll group — and the position is a pure
   function of the **wall clock**, so it is frame-rate independent and never
   eased. The path `d` is rebuilt **once per data change** from the true values
   (no per-frame Y-tween), and the newest point is appended **off-screen** behind
   a one-interval `delay` buffer + `clipPath`, so the visible window only ever
   scrolls into view — it never changes shape instantly.

   **The velocity is driven by the MEASURED data cadence, not a hardcoded
   `tweenMs`.** The engine records each datum's arrival time and EMAs the deltas
   into a smoothed interval; the slide velocity is `slotWidth / measuredInterval`.
   That is what makes a **jittery 1 Hz feed** (the Go stats ticker + Wails event
   bus add ±100-200 ms) still glide at a steady speed: a late sample lets the
   phase glide *past* one slot into the buffer (no freeze-then-snap), and the
   leftover phase is carried across the commit seam (no per-tick teleport).
   `tweenMs` is now only the **seed/clamp** for the very first slides before any
   delta is measured — the engine adapts to the true rate within a couple ticks.

```tsx
import { SmoothLine } from '@djangocfg/ui-tools/smooth-line';

// stats charts tick ≈ 1 Hz
<SmoothLine values={rtt} color="info" tweenMs={1000} area />

// token bridge — inherit a text-* className tint (cmdop's text-chart-3)
<span className="text-chart-3">
  <SmoothLine values={rtt} color="currentColor" />
</span>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `values` | `readonly number[]` | — | Series, oldest-first. Empty → flat baseline. |
| `color` | `SmoothLineColor` | `'primary'` | Semantic token, or `'currentColor'` to inherit a `text-*` tint. |
| `width` | `number` | `240` | viewBox width (SVG stretches to its container). |
| `height` | `number` | `40` | viewBox height (px). |
| `strokeWidth` | `number` | `1.5` | Line stroke. |
| `area` | `boolean` | `false` | Alpha area fill under the line. |
| `tweenMs` | `number` | `1000` | **Seed** cadence (ms) for the scroll velocity + the clamp band — NOT a fixed slide speed. The engine measures the real inter-sample interval and drives the velocity off that. Pass the rough expected cadence (stats ≈ 1000, quality ≈ 30000). |
| `scroll` | `boolean` | `false` | Continuous constant-velocity left-scroll for live windowed charts. |
| `delay` | `boolean` | `true` | Hold the right edge back one interval (buffer the newest point off-screen) so it scrolls in cleanly instead of "grow then snap". Requires `scroll`. |
| `tension` | `number` | `0.5` | Curve smoothness (the line SHAPE). `0` → straight `L` segments; `0.5` → flowing curve; `1` → loosest. |
| `ariaLabel` | `string` | — | Accessible label. |

### Curve smoothing — for host-bespoke charts

The Catmull-Rom → bezier converter is exported so host charts that build their
own geometry (cmdop's TrafficChart mirror areas) can get the same flowing curve:

```ts
import { smoothLinePath, smoothSegments } from '@djangocfg/ui-tools/smooth-line';

// full path through points (line stroke)
const d = smoothLinePath(points, 0.5, { width, height });
// just the C-segments (so an area fill can reuse the exact same curve)
const body = smoothSegments(points, 0.5, { width, height });
```

The **ECG keeps its bespoke SHARP builder** (sharp QRS pulses) and does NOT use
this — a cardiogram needs sharp pulses, not rounded blobs. It reuses only the
glide+scroll engine (`useSmoothSeries`), not the curve smoothing.

## `useSmoothSeries`

The rAF engine is exported as a hook so host-bespoke charts (e.g. cmdop's ECG,
which keeps its own QRS geometry) can reuse the same glide + scroll driver:

```tsx
const { pathRef, scrollRef, staticPath } = useSmoothSeries({
  values, tweenMs: 1000, scroll: true, width: 240, buildPath: buildMyGeometry,
});
```

`buildPath` receives the true values **once per data change** (not per frame) and
returns the `d` string; only the scroll transform updates per frame. The velocity
is self-measured from the data cadence (see above), so hosts don't need an exact
`tweenMs`. Guards (reduced-motion fallback to instant, pause on `document.hidden`)
are built in; `staticPath` is the initial / reduced-motion render value.

Storybook: `apps/storybook/stories/ui-tools/visual/SmoothLine.stories.tsx`
