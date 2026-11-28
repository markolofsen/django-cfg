/**
 * CSP Vendor Presets
 *
 * The problem this solves: every third-party script a DjangoCFG app loads needs
 * its origin named in the CSP, and until now each app had to hand-list those
 * origins (`csp: { scriptSrc: [...] }`) in its own `next.config.ts`. That
 * repeats the same Stripe/Cloudflare/Google origin strings across every app,
 * and — worse — nobody remembers which directive a given vendor needs, so the
 * usual outcome is a production-only console error and a scramble.
 *
 * Instead, apps declare WHAT THEY USE by name (`csp: { vendors: ['stripe'] }`)
 * and this registry owns WHICH ORIGINS that implies. When a vendor changes a
 * host, it is fixed once here and every app inherits the fix on its next build.
 *
 * Adding a vendor: add an entry below, keyed by a short stable name, listing
 * only the directives it genuinely needs. Keep the origins exact — never widen
 * a directive to a bare `https:` to make a vendor work.
 */

/** The CSP directives a vendor preset may contribute origins to. */
export interface CspOrigins {
  /** `script-src` — the vendor's SDK/tag `<script>` hosts. */
  scriptSrc?: string[];
  /** `frame-src` — hosts the vendor mounts iframes from. */
  frameSrc?: string[];
  /** `connect-src` — hosts the vendor makes XHR/fetch/WebSocket calls to. */
  connectSrc?: string[];
  /** `img-src` — hosts the vendor loads images/pixels from. */
  imgSrc?: string[];
  /** `font-src` — hosts the vendor loads web fonts from. */
  fontSrc?: string[];
}

/**
 * Known third-party vendors and the CSP origins each one requires.
 *
 * Every entry is OFF by default — an app opts in via `csp.vendors`, so an app
 * that mounts nothing third-party keeps the tightest possible policy.
 */
export const CSP_VENDOR_PRESETS = {
  /**
   * Stripe.js / Checkout / Elements.
   *
   * `js.stripe.com` serves the SDK and also hosts the Elements iframes;
   * `checkout.stripe.com` is the hosted Checkout iframe; `api.stripe.com`
   * takes the tokenization/confirm XHR. Without all three the payment form
   * silently fails to render.
   */
  stripe: {
    scriptSrc: ['https://js.stripe.com'],
    frameSrc: ['https://js.stripe.com', 'https://checkout.stripe.com'],
    connectSrc: ['https://api.stripe.com'],
  },

  /**
   * Cloudflare Web Analytics (the RUM beacon).
   *
   * IMPORTANT: this script is NOT in the app's own HTML — when Web Analytics
   * is enabled on the zone, Cloudflare INJECTS `beacon.min.js` into the
   * response at the edge, after Next.js has already emitted the CSP header.
   * So any app served through a Cloudflare zone with that feature on will
   * violate its own CSP unless this preset is enabled, no matter what the
   * source tree contains. The beacon also POSTs its payload back to
   * `cloudflareinsights.com`, hence the `connect-src` entry.
   */
  cloudflare: {
    scriptSrc: ['https://static.cloudflareinsights.com'],
    connectSrc: ['https://cloudflareinsights.com', 'https://static.cloudflareinsights.com'],
  },

  /** Google Analytics 4 / gtag.js. */
  'google-analytics': {
    scriptSrc: ['https://www.googletagmanager.com', 'https://www.google-analytics.com'],
    connectSrc: [
      'https://www.google-analytics.com',
      'https://analytics.google.com',
      'https://region1.google-analytics.com',
    ],
    imgSrc: ['https://www.google-analytics.com', 'https://www.googletagmanager.com'],
  },

  /** Google Tag Manager (the container itself; tags it loads may need more). */
  'google-tag-manager': {
    scriptSrc: ['https://www.googletagmanager.com'],
    connectSrc: ['https://www.googletagmanager.com'],
    imgSrc: ['https://www.googletagmanager.com'],
    frameSrc: ['https://www.googletagmanager.com'],
  },

  /** Google Fonts (stylesheet host + the font files themselves). */
  'google-fonts': {
    fontSrc: ['https://fonts.gstatic.com'],
  },

  /** Sentry browser SDK — errors/traces are POSTed to the ingest host. */
  sentry: {
    connectSrc: ['https://*.ingest.sentry.io', 'https://*.sentry.io'],
  },

  /** YouTube embeds (privacy-enhanced host included). */
  youtube: {
    frameSrc: ['https://www.youtube.com', 'https://www.youtube-nocookie.com'],
    imgSrc: ['https://i.ytimg.com'],
  },

  /** Vimeo embeds. */
  vimeo: {
    frameSrc: ['https://player.vimeo.com'],
    imgSrc: ['https://i.vimeocdn.com'],
  },
} as const satisfies Record<string, CspOrigins>;

/** Name of a vendor preset in {@link CSP_VENDOR_PRESETS}. */
export type CspVendor = keyof typeof CSP_VENDOR_PRESETS;

/**
 * Vendors applied to every app unless explicitly disabled.
 *
 * The rule for this list: an origin belongs here when the app CANNOT DECLARE IT
 * FROM `next.config.ts`, because whatever turns the script on lives somewhere
 * the config file cannot read. Leaving such a vendor opt-in does not produce a
 * build error or a dev warning — it produces a production-only console error
 * that nobody sees until a user reports a broken page.
 *
 * - `cloudflare` — the Web Analytics beacon is rewritten into the HTML AT THE
 *   EDGE, after Next.js has already sent the CSP header. Nothing in the source
 *   tree reveals it. (Observed 2026-07-22: all six DjangoCFG-served hosts were
 *   violating their own CSP.)
 *
 * - `google-analytics` — gtag.js is injected AT RUNTIME by `@djangocfg/layouts`
 *   (`BaseApp analytics={{ googleTrackingId }}` → the lazy `ga4()` transport).
 *   That id is an ordinary TS value in the app's `settings.ts`, not an env var,
 *   so `next.config.ts` — a different module, evaluated in a different process,
 *   before any of that code runs — has no way to see whether GA is on. The app
 *   author enables analytics in one file and silently breaks CSP in another.
 *   (Observed 2026-07-23: cmdop `apps/web` blocked on
 *   `googletagmanager.com/gtag/js?id=G-YJ0F48S83F`.)
 *
 * - `youtube` / `vimeo` — these existed for `VideoPlayer`
 *   (`@djangocfg/ui-tools`), which mounted the iframes AT RUNTIME from a URL
 *   inside a chat message. That player was retired with `ui-tools`;
 *   `@djangocfg/widget-player` embeds no third-party frames, so **nothing in
 *   this repo needs these presets today**. They are kept because the shape of
 *   the problem outlives the component: an app author enables a chat, and
 *   whether a user ever pastes a YouTube link is not knowable at build time,
 *   so no `next.config.ts` can declare it honestly.
 *
 * Note what these have in common: the script/frame is turned on by the RUNTIME
 * (the edge, a package, or an end user), never by the app author editing the
 * config. Stripe is the counter-example and deliberately NOT here — a developer
 * decides to mount a payment form, knows they did, and can say `vendors:
 * ['stripe']`; putting it in the baseline would hand `frame-src js.stripe.com`
 * to marketing sites that never take a payment.
 *
 * Do NOT add ordinary third parties here — anything an app knowingly mounts and
 * can name in its own config belongs in `csp.vendors`, so unrelated apps keep
 * the tighter policy. The cost of an entry here is that every app permits these
 * hosts; that is only worth paying when the alternative is silent breakage.
 */
export const CSP_BASELINE_VENDORS: CspVendor[] = [
  'cloudflare',
  'google-analytics',
  'youtube',
  'vimeo',
];

/**
 * Merge the named vendor presets into a single set of extra origins.
 *
 * Unknown names are ignored rather than thrown on: a typo must not break the
 * production build of an app whose only mistake was a misspelled analytics
 * vendor. `warnUnknown` surfaces them on the build log instead.
 */
export function resolveCspVendors(
  vendors: readonly string[] | undefined,
  warnUnknown = true
): CspOrigins {
  const merged: Required<CspOrigins> = {
    scriptSrc: [],
    frameSrc: [],
    connectSrc: [],
    imgSrc: [],
    fontSrc: [],
  };

  if (!vendors?.length) return merged;

  const unknown: string[] = [];

  for (const name of vendors) {
    const preset = (CSP_VENDOR_PRESETS as Record<string, CspOrigins>)[name];
    if (!preset) {
      unknown.push(name);
      continue;
    }
    for (const key of Object.keys(merged) as (keyof Required<CspOrigins>)[]) {
      const origins = preset[key];
      if (origins) merged[key].push(...origins);
    }
  }

  if (unknown.length && warnUnknown) {
    const known = Object.keys(CSP_VENDOR_PRESETS).join(', ');
    console.warn(
      `[djangocfg] Unknown CSP vendor(s): ${unknown.join(', ')}. Known vendors: ${known}`
    );
  }

  // De-duplicate so two presets sharing a host (e.g. GA + GTM both using
  // googletagmanager.com) don't emit it twice in the header.
  for (const key of Object.keys(merged) as (keyof Required<CspOrigins>)[]) {
    merged[key] = [...new Set(merged[key])];
  }

  return merged;
}
