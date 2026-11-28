import assert from 'node:assert/strict'
import { test } from 'node:test'

import { createMetadata, type SiteMetaConfig } from './metadata-factory'

/**
 * `canonical` and `og:url` name the SAME page. The bug this suite locks down is
 * that they were built by two different template literals with opposite slash
 * conventions, so they silently disagreed:
 *
 *   canonical: `${siteUrl}/${path}`   // path "/skills" -> "site.com//skills"
 *   og:url:    `${siteUrl}${path}`    // path "skills"  -> "site.comskills"
 *
 * A consumer that "fixed" one by reshaping `path` at the call site necessarily
 * broke the other. So every case below asserts BOTH tags together — that
 * pairing is the actual invariant, not either URL on its own.
 */

const BASE: SiteMetaConfig = {
  name: 'Marketplace',
  description: 'Capability catalogue',
  siteUrl: 'https://marketplace.cmdop.com',
  ogImage: '/opengraph-image',
}

const LOCALIZED: SiteMetaConfig = {
  ...BASE,
  siteUrl: 'https://cmdop.com',
  locales: ['en', 'de'],
  defaultLocale: 'en',
}

/** Reads back the two URLs the factory is supposed to keep in lock-step. */
function urlsFor(config: SiteMetaConfig, page: Parameters<typeof createMetadata>[1]) {
  const meta = createMetadata(config, page)
  const alternates = meta.alternates as { canonical?: string; languages?: Record<string, string> }
  const openGraph = meta.openGraph as { url?: string } | undefined
  return { canonical: alternates?.canonical, ogUrl: openGraph?.url, languages: alternates?.languages }
}

/** The single invariant: both tags point at the one expected URL. */
function assertBoth(
  config: SiteMetaConfig,
  page: Parameters<typeof createMetadata>[1],
  expected: string
) {
  const { canonical, ogUrl } = urlsFor(config, page)
  assert.equal(canonical, expected, 'canonical')
  assert.equal(ogUrl, expected, 'og:url')
  assert.equal(canonical, ogUrl, 'canonical and og:url must agree')
}

// ── no locales (marketplace, llm, mark) ──────────────────────────────────────

test('no-locale + home (path: "") → bare site URL', () => {
  assertBoth(BASE, { title: 'Home', path: '' }, 'https://marketplace.cmdop.com')
})

test('no-locale + home (path omitted) → bare site URL', () => {
  assertBoth(BASE, { title: 'Home' }, 'https://marketplace.cmdop.com')
})

test('no-locale + home (path: "/") → bare site URL, not a trailing slash', () => {
  // `routes.home` is literally '/' in apps/marketplace, so this is a real input.
  assertBoth(BASE, { title: 'Home', path: '/' }, 'https://marketplace.cmdop.com')
})

test('no-locale + "/skills" → one slash, not two, not zero', () => {
  assertBoth(BASE, { title: 'Skills', path: '/skills' }, 'https://marketplace.cmdop.com/skills')
})

test('no-locale + nested "/skills/foo" → the live bug: og:url glued the domain to the path', () => {
  assertBoth(
    BASE,
    { title: 'Foo', path: '/skills/foo' },
    'https://marketplace.cmdop.com/skills/foo'
  )
})

// ── locales (web) ────────────────────────────────────────────────────────────

test('locale + home → origin + locale only', () => {
  assertBoth(LOCALIZED, { title: 'Home', path: '', locale: 'en' }, 'https://cmdop.com/en')
})

test('locale + "/pricing" → origin + locale + path', () => {
  assertBoth(
    LOCALIZED,
    { title: 'Pricing', path: '/pricing', locale: 'de' },
    'https://cmdop.com/de/pricing'
  )
})

test('locale + nested path', () => {
  assertBoth(
    LOCALIZED,
    { title: 'Terms', path: '/legal/terms', locale: 'en' },
    'https://cmdop.com/en/legal/terms'
  )
})

test('locale hreflang alternates are built by the same rule', () => {
  const { languages } = urlsFor(LOCALIZED, { title: 'Pricing', path: '/pricing', locale: 'en' })
  assert.deepEqual(languages, {
    en: 'https://cmdop.com/en/pricing',
    de: 'https://cmdop.com/de/pricing',
    'x-default': 'https://cmdop.com/en/pricing',
  })
})

test('locale hreflang alternates at home carry no trailing slash', () => {
  const { languages } = urlsFor(LOCALIZED, { title: 'Home', path: '', locale: 'en' })
  assert.deepEqual(languages, {
    en: 'https://cmdop.com/en',
    de: 'https://cmdop.com/de',
    'x-default': 'https://cmdop.com/en',
  })
})

// ── normalization guards ─────────────────────────────────────────────────────

test('a trailing slash on the site URL does not double up', () => {
  assertBoth(
    { ...BASE, siteUrl: 'https://marketplace.cmdop.com/' },
    { title: 'Skills', path: '/skills' },
    'https://marketplace.cmdop.com/skills'
  )
})

test('an off-contract slash-less path still yields a well-formed URL', () => {
  // The old consumer wrapper stripped the leading slash before calling the
  // factory. That workaround is gone, but a call site that passes 'skills'
  // must still not produce "site.comskills".
  assertBoth(BASE, { title: 'Skills', path: 'skills' }, 'https://marketplace.cmdop.com/skills')
})
