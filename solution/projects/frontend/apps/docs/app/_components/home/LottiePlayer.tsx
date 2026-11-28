'use client';

import { useEffect, useRef, useState } from 'react';
import Lottie from 'react-lottie-player';

/**
 * Minimal Lottie player for the landing hero — purpose-built, no extra deps
 * beyond react-lottie-player.
 *
 * - Loads the animation JSON from a URL (kept out of the JS bundle; served
 *   from /public).
 * - Autoplays + loops by default, but only once it scrolls into view.
 * - Respects `prefers-reduced-motion`: shows a static first frame instead of
 *   animating.
 */
export interface LottiePlayerProps {
  /** URL to the Lottie JSON (e.g. /lottie/coding.json). */
  src: string;
  loop?: boolean;
  speed?: number;
  className?: string;
  ariaLabel?: string;
  /**
   * SVG fit mode. 'meet' (default) shows the whole animation with letterboxing;
   * 'slice' fills the box edge-to-edge and crops the overflow.
   */
  fit?: 'meet' | 'slice';
}

export function LottiePlayer({
  src,
  loop = true,
  speed = 1,
  className,
  ariaLabel = 'Animation',
  fit = 'meet',
}: LottiePlayerProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<object | null>(null);
  const [inView, setInView] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(false);

  // Fetch the animation JSON once (kept out of the bundle).
  useEffect(() => {
    let alive = true;
    fetch(src)
      .then((r) => r.json())
      .then((json) => {
        if (alive) setData(json);
      })
      .catch(() => {
        /* decorative — fail silently */
      });
    return () => {
      alive = false;
    };
  }, [src]);

  // Respect prefers-reduced-motion (and react to changes).
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => setReduceMotion(mq.matches);
    update();
    mq.addEventListener('change', update);
    return () => mq.removeEventListener('change', update);
  }, []);

  // Only animate while in the viewport.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => setInView(entry.isIntersecting),
      { threshold: 0.1 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <div ref={ref} className={className} role="img" aria-label={ariaLabel}>
      {data && (
        <Lottie
          animationData={data}
          play={inView && !reduceMotion}
          loop={loop && !reduceMotion}
          speed={speed}
          goTo={reduceMotion ? 0 : undefined}
          style={{ width: '100%', height: '100%' }}
          rendererSettings={{ preserveAspectRatio: `xMidYMid ${fit}` }}
        />
      )}
    </div>
  );
}
