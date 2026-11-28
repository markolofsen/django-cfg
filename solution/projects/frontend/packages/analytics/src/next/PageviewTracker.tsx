'use client'

/**
 * Next.js App Router pageview tracking.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * WHY THE <Suspense> BOUNDARY IS MANDATORY
 * ─────────────────────────────────────────────────────────────────────────────
 * `useSearchParams()` without a Suspense boundary above it de-opts the ENTIRE
 * page into client-side rendering. Not this component — the whole page. It is
 * silent, and it is a repo-wide performance regression that shows up as a
 * mysteriously worse Lighthouse score weeks later.
 *
 * `usePathname()` is exempt; only `useSearchParams()` triggers it.
 * `@vercel/analytics` wraps its own tracker in Suspense for exactly this reason.
 *
 * So the inner component is never exported. The exported one is already wrapped.
 */

import { usePathname, useSearchParams } from 'next/navigation'
import { Suspense, useEffect } from 'react'

import { useAnalyticsClient } from '../react/context'

export interface PageviewTrackerProps {
  /**
   * The templated route, e.g. `/[locale]/blog/[slug]`.
   *
   * Next does not expose this to client components, so the app must pass it.
   * Without it, `/en/pricing` and `/ru/pricing` are counted as two different
   * pages, which makes the top-pages report useless on a locale-prefixed site.
   */
  route?: string

  /** Current locale, lifted into its own dimension rather than fused into the path. */
  locale?: string
}

function Tracker({ route, locale }: PageviewTrackerProps) {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const client = useAnalyticsClient()

  useEffect(() => {
    if (!client || !pathname) return

    const search = searchParams?.toString() ?? ''
    const params = new URLSearchParams(search)

    client.trackPageview({
      event_name: 'pageview',
      pathname,
      route,
      locale,
      hostname: window.location.hostname,
      page_title: document.title,
      // Only the FIRST pageview of a visit has a meaningful referrer; on
      // subsequent client-side navigations document.referrer still holds the
      // original external referrer, which is what we want for attribution.
      referrer: document.referrer,
      utm_source: params.get('utm_source') ?? undefined,
      utm_medium: params.get('utm_medium') ?? undefined,
      utm_campaign: params.get('utm_campaign') ?? undefined,
      utm_content: params.get('utm_content') ?? undefined,
      utm_term: params.get('utm_term') ?? undefined,
      ...extractClickId(params),
      // `search` feeds the client's dedup key, so ?page=2 counts as a new
      // pageview while router.refresh() does not.
      props: { search: search ? `?${search}` : '' },
    })
  }, [client, pathname, searchParams, route, locale])

  return null
}

/** Known ad-platform click ids. One column pair server-side, not six. */
const CLICK_ID_PARAMS = ['gclid', 'fbclid', 'msclkid', 'ttclid', 'li_fat_id', 'twclid']

function extractClickId(params: URLSearchParams) {
  for (const key of CLICK_ID_PARAMS) {
    const value = params.get(key)
    if (value) return { click_id: value, click_id_param: key }
  }
  return {}
}

export function PageviewTracker(props: PageviewTrackerProps) {
  return (
    <Suspense fallback={null}>
      <Tracker {...props} />
    </Suspense>
  )
}
