// useSmoothSeries — the CANVAS streaming-chart engine shared by SmoothLine
// (generic) and by host-bespoke charts (e.g. cmdop's ECG, which keeps its own
// QRS geometry but reuses this scroll driver).
//
// THE CANVAS MODEL (Smoothie / uPlot / Grafana — one writer, one clock):
// every rAF frame we `clearRect` the whole canvas and redraw the ENTIRE line at
// its current wall-clock-scrolled X. The "new point arrived" and "everything
// scrolled" are the SAME per-frame draw — there is no second thing to fall out
// of sync, so the jump-then-catch-up is impossible BY CONSTRUCTION.
//
// WHY WE LEFT SVG-transform (the bug this rewrite kills):
// The old engine animated TWO independent things on TWO clocks that had to agree
// every frame:
//   (1) the SVG path `d` — rebuilt in a React effect ONCE per data tick (≈1 Hz,
//       jittery), in data-space; and
//   (2) the `<g>` transform — animated EVERY rAF frame (60 Hz) off the wall clock.
// The on-screen position of a point was `pathX(point) + transformX(frame)`. Those
// two writes land in DIFFERENT frames on DIFFERENT clocks — at the data-tick seam
// the path jumped one slot left while the transform's phase-reset landed a frame
// early/late → a one-frame double-shift (JUMP) then the transform gliding back
// (slow CATCH-UP). That was the user's "jump then slowly catch up to the right".
// No amount of EMA / delay / clipPath tuning could close it because the root was
// the two-writer/two-clock split, not a tuning bug. Canvas removes the split.
//
// WHAT WE KEEP (the parts that already worked — they were never the bug):
//   • MEASURED cadence (EMA of inter-sample arrival deltas) → estimates the real
//     feed rate so a jittery 1-Hz feed still glides at roughly the right speed (no
//     hardcoded tweenMs for the slide).
//   • DELAY/LAG — hold the freshest sample one interval off the right edge so the
//     next point is already known before we draw it (Smoothie `delay`). On canvas
//     the off-edge point simply sits past `width` and the scroll slides it in; no
//     clipPath needed — `clearRect` to the canvas box clips for free.
//   • CARRY across the commit seam — the fractional glide still in flight at a
//     commit is carried, never snapped to 0, so the scroll is continuous.
//   • prefers-reduced-motion → a single static draw (no loop); pause on
//     document.hidden.
//
// RESIDUAL-JITTER POLISH (the micro-wobble this revision kills):
// The canvas rewrite removed the big jerk, but a slight wobble remained. Its root:
// the per-frame scroll VELOCITY was `slotW / measuredInterval`, and `measuredInterval`
// is an EMA recomputed on EVERY sample. A jittery feed nudged that EMA tick-to-tick,
// so the visible scroll speed micro-adjusted at every commit seam — a perceptible
// "поддёргивание". The professional fix (Smoothie / uPlot / Grafana): DECOUPLE the
// visible velocity from per-sample timing.
//   • SLEWED velocity — the rAF loop scrolls off `effectiveIntervalRef`, a value
//     that creeps SLOWLY toward the EMA target (a small fraction per frame). The
//     EMA still tracks the cadence for adaptation, but the on-screen speed only
//     ever changes imperceptibly — no per-tick snap. The `delay` BUFFER (not the
//     velocity) absorbs the arrival jitter.
//   • LARGER delay buffer — phase may glide further past 1.0 (≈1.8 slots of slack
//     instead of ~1.35) so a late/early sample is swallowed by the buffer long
//     before it could perturb the visible scroll.
//   • CONSISTENT frame timestamp — the rAF callback uses its OWN `time` arg for the
//     phase calc, so there is no `performance.now()` drift between sub-steps of one
//     frame. The commit effect still stamps with `performance.now()` (it runs
//     outside rAF); the loop reconciles both on the same monotonic clock.
//   • C0-CONTINUOUS commit seam — the carry keeps the fractional leftover so the
//     scroll position never hops across a commit.
//
// THE PER-FRAME LOOP (one writer, one clock):
//   1. now = rAF time arg (one clock, one timestamp per frame)
//   2. phase = carry + (now − lastCommit) / effectiveInterval  // slots, wall-clock
//   3. scrollX = −slotW · (1 − clampedPhase)                    // px, ≤ 0
//   4. dpr-scale the ctx, clearRect the box, call host draw(ctx, { scrollX, … })
//   The host draws point i at `i·slotW + scrollX` — newest point sits just past
//   the right edge and slides in; oldest fall off the left. Same geometry the SVG
//   builders drew, now emitted to ctx via moveTo/lineTo/bezierCurveTo.

'use client';

import * as React from 'react';

/** SSR-safe `prefers-reduced-motion: reduce` subscription. */
export function useReducedMotion(): boolean {
  const [reduced, setReduced] = React.useState(false);

  React.useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => setReduced(mq.matches);
    update();
    mq.addEventListener('change', update);
    return () => mq.removeEventListener('change', update);
  }, []);

  return reduced;
}

/**
 * Per-frame draw context handed to the host's {@link DrawFn}. All coordinates are
 * in CSS pixels over the chart's logical `width × height` box — the engine has
 * already applied the `devicePixelRatio` transform to the `ctx`, so the host
 * draws in plain logical units and gets crisp retina output for free.
 */
export interface DrawContext {
  /**
   * The current wall-clock scroll offset, in CSS px (≤ 0). Add it to each point's
   * data-space X so the trace slides left: the host draws point `i` at
   * `i·slotWidth + scrollX`. At a fresh commit `scrollX ≈ −slotWidth` (newest
   * point one slot off the right edge) and glides to `0` over one interval.
   */
  scrollX: number;
  /** Per-slot scroll distance in CSS px (`width / (drawnCount − 1)`), or 0. */
  slotWidth: number;
  /** Logical chart width in CSS px (the consumer's `width` prop / viewBox). */
  width: number;
  /** Logical chart height in CSS px. */
  height: number;
  /** Device pixel ratio the ctx is scaled by (host rarely needs it). */
  dpr: number;
}

/**
 * Host-supplied per-frame draw. Called after the engine has sized + dpr-scaled
 * the ctx and `clearRect`-ed the box. The host strokes/fills its geometry at the
 * scrolled X. SmoothLine passes a monotone-cubic polyline drawer; the ECG passes
 * its bespoke QRS drawer (three colour passes in one callback).
 *
 * The draw receives the CURRENT committed values via closure (the host rebuilds
 * the callback when `values`/`epoch` change), so there is no per-frame Y-tween —
 * the shape is fixed between ticks, only the window scrolls.
 */
export type DrawFn = (ctx: CanvasRenderingContext2D, frame: DrawContext) => void;

export interface SmoothSeriesConfig {
  /** Target series, oldest-first. A change advances the scroll + redraws. */
  values: readonly number[];
  /**
   * Seed cadence (ms) for the scroll velocity — used ONLY as the initial guess
   * and the floor/ceiling clamp bounds, NOT as the fixed slide speed. The engine
   * MEASURES the real inter-sample interval (an EMA of the deltas between datum
   * arrivals) as a cadence target, then SLEWS the visible scroll velocity slowly
   * toward it — so a jittery 1 Hz feed glides at a rock-steady speed (the velocity
   * is decoupled from per-sample timing; the `delay` buffer absorbs the jitter).
   * Pass the rough expected cadence (stats ≈ 1000, a 30 s quality series ≈ 30000).
   * @default 1000
   */
  tweenMs?: number;
  /**
   * Continuous left-scroll. When set, the engine drives a constant-velocity
   * wall-clock scroll so the window slides like a hospital monitor instead of
   * teleporting. `slotWidth` is derived from `width / (drawnCount − 1)`. When
   * false the engine still draws (static), it just never scrolls. @default false
   */
  scroll?: boolean;
  /** Logical chart width (CSS px) used to derive the scroll slot-width. @default 240 */
  width?: number;
  /** Logical chart height (CSS px). @default 40 */
  height?: number;
  /**
   * Optional retarget trigger. The engine normally advances when the numeric
   * `values` change. A sliding window of IDENTICAL tokens (e.g. a steady ECG
   * ok-stream where the envelope stays all-1s) produces no numeric change, so the
   * scroll would never advance. Bump `epoch` once per tick (the host's sample
   * count works well) to advance the scroll even when `values` are unchanged.
   */
  epoch?: number;
  /**
   * Hold the right edge back by one interval so the newest point is already known
   * before it scrolls into view (Smoothie / chartjs-streaming `delay`). When set,
   * the freshest value is dropped from the drawn set and lives off the right edge,
   * revealed only by the scroll — so the right edge reads as a continuous stream
   * instead of "growing then snapping". Requires `scroll`. @default true
   */
  delay?: boolean;
  /**
   * Per-frame draw callback (host geometry). The drawn values are passed via
   * closure — see {@link DrawFn}. The host should rebuild this (`useMemo` /
   * `useCallback`) when its committed values or styling change.
   */
  draw: DrawFn;
}

export interface SmoothSeriesHandles {
  /** Attach to the `<canvas>` the engine sizes (dpr) and drives. */
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  /**
   * Force one static redraw at scrollX = 0 (newest point flush at the right edge).
   * The engine calls this itself on reduced-motion / resize / `scroll=false`; the
   * host rarely needs it, but it is exposed for an imperative refresh.
   */
  redraw: () => void;
}

/**
 * Drive a constant-velocity CANVAS streaming line from a changing `values` array.
 *
 * Returns a `canvasRef` the host attaches to one `<canvas>`. The engine sizes the
 * canvas to its box × devicePixelRatio, runs a single persistent wall-clock rAF
 * loop, and every frame `clearRect`s and calls the host `draw` at the current
 * scroll offset — one writer, one clock, so the SVG-era jump-then-catch-up cannot
 * occur. On reduced-motion / `scroll=false` it never starts the loop and renders
 * a single static frame.
 */
export function useSmoothSeries(config: SmoothSeriesConfig): SmoothSeriesHandles {
  const {
    values,
    tweenMs = 1000,
    scroll = false,
    width = 240,
    height = 40,
    epoch,
    delay = true,
    draw,
  } = config;

  const reduced = useReducedMotion();

  const canvasRef = React.useRef<HTMLCanvasElement | null>(null);

  // Latest draw callback without retriggering effects every render.
  const drawRef = React.useRef(draw);
  drawRef.current = draw;

  const targetKey = React.useMemo(() => values.join(','), [values]);

  // With `delay` on we draw the buffer MINUS its freshest point so the right edge
  // is always a point we already know — the newest value lives off the right edge,
  // revealed by the scroll. One slot of room is the lag.
  const useLag = scroll && delay && values.length > 2;
  const drawnCount = useLag ? Math.max(0, values.length - 1) : values.length;

  // Slot width: the per-tick scroll distance, in logical (CSS) px.
  const slotW = React.useMemo(() => {
    if (!scroll) return 0;
    return drawnCount > 1 ? width / (drawnCount - 1) : 0;
  }, [scroll, drawnCount, width]);
  const slotWRef = React.useRef(slotW);
  slotWRef.current = slotW;

  // Seed cadence — the floor/ceiling clamp and the initial guess for the EMA.
  const seedIntervalRef = React.useRef(Math.max(1, tweenMs));
  seedIntervalRef.current = Math.max(1, tweenMs);

  // MEASURED cadence (EMA of inter-sample deltas). This is the cadence ESTIMATE
  // that tracks the feed rate; it is NOT what the visible scroll runs off directly
  // (that micro-wobbles on a jittery feed). It is the slew TARGET for the velocity.
  const measuredIntervalRef = React.useRef(Math.max(1, tweenMs));
  // EFFECTIVE cadence — what the visible scroll velocity actually uses. It creeps
  // slowly toward `measuredInterval` (a few % per frame), so the on-screen speed
  // never snaps tick-to-tick even when the EMA wobbles. This is the residual-jitter
  // fix: the velocity is decoupled from per-sample timing; the `delay` buffer eats
  // the arrival jitter, not the velocity.
  const effectiveIntervalRef = React.useRef(Math.max(1, tweenMs));
  // Wall-clock timestamp of the LAST commit (datum arrival). The scroll phase is a
  // pure function of (now − lastCommit) / measuredInterval — position is driven by
  // wall-clock, not by integrating per-frame dt (which drifts). Self-correcting: a
  // slow frame just lands further along the same line.
  const lastCommitRef = React.useRef<number>(0);
  // Carry-over phase: the fractional glide still in flight at the moment of a
  // commit. We DON'T snap it to 0 — we keep gliding from the leftover so the
  // scroll never teleports across the commit seam (chartjs `preservation`).
  const carryRef = React.useRef<number>(0);

  // The DPR the canvas backing store is currently sized for.
  const dprRef = React.useRef(1);

  // ── Size the canvas backing store to box × devicePixelRatio and scale the ctx
  // so all host drawing is in logical (CSS) px and stays crisp on retina. Returns
  // a ready, cleared, dpr-scaled 2D context (or null pre-mount / SSR).
  const prepareCtx = React.useCallback((): CanvasRenderingContext2D | null => {
    const canvas = canvasRef.current;
    if (!canvas || typeof window === 'undefined') return null;

    const dpr = Math.max(1, window.devicePixelRatio || 1);
    // Logical size: width/height props (the viewBox), but the canvas stretches to
    // its container width via CSS — so prefer the measured client box when laid
    // out, falling back to the prop box pre-layout.
    const cssW = canvas.clientWidth || width;
    const cssH = canvas.clientHeight || height;
    const bw = Math.round(cssW * dpr);
    const bh = Math.round(cssH * dpr);
    if (canvas.width !== bw) canvas.width = bw;
    if (canvas.height !== bh) canvas.height = bh;
    dprRef.current = dpr;

    const ctx = canvas.getContext('2d');
    if (!ctx) return null;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, bw, bh);
    // Scale logical→device, AND map the logical `width` (viewBox) onto the
    // measured CSS width so geometry built against `width` stretches to fill the
    // container — the canvas analogue of SVG `preserveAspectRatio="none"`.
    const sx = (cssW / width) * dpr;
    const sy = (cssH / height) * dpr;
    ctx.setTransform(sx, 0, 0, sy, 0, 0);
    return ctx;
  }, [width, height]);

  // ── One static draw at scrollX = 0 (newest point flush at the right edge). Used
  // for reduced-motion, scroll=false, and resize. Geometry is in logical units.
  const redraw = React.useCallback(() => {
    const ctx = prepareCtx();
    if (!ctx) return;
    drawRef.current(ctx, {
      scrollX: 0,
      slotWidth: slotWRef.current,
      width,
      height,
      dpr: dprRef.current,
    });
  }, [prepareCtx, width, height]);

  // ── Measure the inter-sample interval on every data advance (EMA) and commit.
  React.useEffect(() => {
    if (typeof window === 'undefined') return;
    const now =
      typeof performance !== 'undefined' ? performance.now() : Date.now();

    if (lastCommitRef.current > 0) {
      const deltaMs = now - lastCommitRef.current;
      // Ignore absurd deltas (backgrounded tab → huge gap; double-fire → ~0).
      // Clamp to a generous band (¼×…4×) around the seed so a single outlier
      // can't whip the velocity but genuine cadence changes still adapt.
      const lo = seedIntervalRef.current / 4;
      const hi = seedIntervalRef.current * 4;
      if (deltaMs >= lo && deltaMs <= hi) {
        const alpha = 0.25; // ~4-sample memory
        measuredIntervalRef.current =
          alpha * deltaMs + (1 - alpha) * measuredIntervalRef.current;
      }
      // Carry the in-flight glide across the seam. At commit the phase has glided
      // to ~1.0 (on time), past (late), or short (early). Keep the FRACTIONAL
      // leftover so the next slot resumes from exactly where this one was — no
      // snap. The drawn set simultaneously loses its oldest / gains a slot, so
      // phase-minus-1 keeps the on-screen position continuous across the seam.
      //
      // The carry MUST be measured against the SAME interval the visible loop
      // scrolls off (the slewed effectiveInterval), not the raw EMA — otherwise a
      // tick-to-tick mismatch between the carry's basis and the loop's basis would
      // re-introduce a sub-pixel seam hop. This keeps the position C0-continuous.
      const phase = deltaMs / effectiveIntervalRef.current;
      carryRef.current = Math.max(-0.25, Math.min(0.5, phase - 1));
    } else {
      carryRef.current = 0;
    }
    lastCommitRef.current = now;
  }, [targetKey, epoch]);

  // ── Static path: when not scrolling (or reduced motion), redraw on any data /
  // geometry change. (When scrolling, the rAF loop owns the canvas.)
  React.useEffect(() => {
    if (scroll && !reduced) return; // the loop owns it
    redraw();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scroll, reduced, targetKey, epoch, width, height]);

  // ── The single persistent wall-clock rAF loop: clearRect → host draw at the
  // current scroll offset, every frame. One writer, one clock.
  React.useEffect(() => {
    if (!scroll || reduced || typeof window === 'undefined') return;

    let raf = 0;
    // How fast the visible velocity creeps toward the measured-cadence target,
    // per frame. Small → the on-screen speed only ever drifts imperceptibly, so a
    // wobbling EMA never shows up as a per-tick velocity snap. A genuine cadence
    // change (e.g. feed slows from 1 Hz → 0.5 Hz) is still tracked, just gently
    // (~60 frames ≈ 1 s to converge ~70%). This is the velocity decouple.
    const VELOCITY_SLEW = 0.02;
    const tick = (time: number) => {
      raf = requestAnimationFrame(tick);
      if (document.hidden) return; // pause while backgrounded (cheap poll)

      const ctx = prepareCtx();
      if (!ctx) return;

      // ONE timestamp per frame, from rAF — used for BOTH the phase calc here and
      // (via lastCommit, stamped on the same monotonic clock) the seam math. No
      // performance.now() drift between sub-steps of a single frame.
      const now = time;

      // Slew the EFFECTIVE interval toward the EMA target a small fraction each
      // frame. The visible scroll runs off THIS, so its velocity changes are
      // gradual — the residual micro-jitter (velocity snapping every commit) is
      // gone. The buffer, not the velocity, absorbs the arrival jitter.
      const target = measuredIntervalRef.current;
      effectiveIntervalRef.current +=
        (target - effectiveIntervalRef.current) * VELOCITY_SLEW;
      const effInterval = effectiveIntervalRef.current || 1;

      let scrollX = 0;
      if (lastCommitRef.current > 0) {
        // Wall-clock phase since the last commit, in slots (Smoothie model — pure
        // function of time, self-correcting, frame-rate independent). `carry` is
        // the leftover from the previous slot so the glide is continuous across
        // the commit seam. A LATE sample lets phase glide PAST 1 into the `delay`
        // buffer (off the right edge, clipped by clearRect) rather than freezing.
        // The buffer is generous (≈1.8 slots) so an early/late arrival is wholly
        // swallowed by slack and never perturbs the visible speed; floor at 0 so
        // an early phase holds the left edge.
        const elapsed = now - lastCommitRef.current;
        const phase = carryRef.current + elapsed / effInterval;
        const pos = Math.min(1.8, Math.max(0, phase));
        scrollX = -slotWRef.current * (1 - pos);
      }

      drawRef.current(ctx, {
        scrollX,
        slotWidth: slotWRef.current,
        width,
        height,
        dpr: dprRef.current,
      });
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [scroll, reduced, width, height, prepareCtx]);

  // ── Redraw on container resize (fluid width). The rAF loop already re-measures
  // every frame when scrolling; this covers the static / reduced-motion case.
  React.useEffect(() => {
    if (typeof window === 'undefined' || typeof ResizeObserver === 'undefined') {
      return;
    }
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ro = new ResizeObserver(() => {
      if (!scroll || reduced) redraw();
    });
    ro.observe(canvas);
    return () => ro.disconnect();
  }, [scroll, reduced, redraw]);

  return { canvasRef, redraw };
}
