/**
 * Mapping of language codes (ISO 639-1) → primary country code (ISO 3166-1 alpha-2).
 *
 * Used to render a country flag SVG for a language code. Many languages are
 * spoken in multiple countries — we pick the most representative one.
 */

import type { TLanguageCode, TCountryCode } from 'countries-list';

export const LANGUAGE_TO_COUNTRY: Partial<Record<TLanguageCode, TCountryCode>> = {
  // Major world languages
  en: 'US',
  zh: 'CN',
  es: 'ES',
  ar: 'SA',
  hi: 'IN',
  bn: 'BD',
  pt: 'BR',
  ru: 'RU',
  ja: 'JP',
  de: 'DE',
  fr: 'FR',
  ko: 'KR',
  it: 'IT',
  tr: 'TR',
  vi: 'VN',
  pl: 'PL',
  uk: 'UA',
  nl: 'NL',

  // European
  el: 'GR',
  cs: 'CZ',
  sv: 'SE',
  hu: 'HU',
  ro: 'RO',
  da: 'DK',
  fi: 'FI',
  no: 'NO',
  nb: 'NO',
  nn: 'NO',
  sk: 'SK',
  bg: 'BG',
  hr: 'HR',
  sr: 'RS',
  sl: 'SI',
  et: 'EE',
  lv: 'LV',
  lt: 'LT',
  be: 'BY',
  mk: 'MK',
  sq: 'AL',
  is: 'IS',
  mt: 'MT',
  ga: 'IE',
  cy: 'GB',
  gd: 'GB',
  br: 'FR',
  lb: 'LU',
  fo: 'FO',
  bs: 'BA',

  // Spanish regional
  eu: 'ES',
  ca: 'ES',
  gl: 'ES',

  // Asian
  th: 'TH',
  id: 'ID',
  ms: 'MY',
  tl: 'PH',
  jv: 'ID',
  su: 'ID',

  // South Asian
  ta: 'IN',
  te: 'IN',
  mr: 'IN',
  gu: 'IN',
  kn: 'IN',
  ml: 'IN',
  pa: 'IN',
  or: 'IN',
  as: 'IN',
  ne: 'NP',
  si: 'LK',
  dz: 'BT',

  // Middle East & Central Asia
  fa: 'IR',
  ur: 'PK',
  ps: 'AF',
  he: 'IL',
  ku: 'IQ',
  hy: 'AM',
  ka: 'GE',
  az: 'AZ',
  kk: 'KZ',
  uz: 'UZ',
  tg: 'TJ',
  ky: 'KG',
  tk: 'TM',
  mn: 'MN',

  // Southeast Asian
  my: 'MM',
  km: 'KH',
  lo: 'LA',

  // African
  sw: 'KE',
  am: 'ET',
  ha: 'NG',
  yo: 'NG',
  ig: 'NG',
  zu: 'ZA',
  xh: 'ZA',
  af: 'ZA',
  st: 'ZA',
  tn: 'BW',
  sn: 'ZW',
  rw: 'RW',
  rn: 'BI',
  so: 'SO',
  ti: 'ER',
  mg: 'MG',
  ny: 'MW',
  lg: 'UG',
  wo: 'SN',
  ff: 'SN',
  bm: 'ML',

  // Caribbean & Creole
  ht: 'HT',

  // Pacific
  mi: 'NZ',
  sm: 'WS',
  to: 'TO',
  fj: 'FJ',
  mh: 'MH',
  ty: 'PF',
  na: 'NR',
  bi: 'VU',
  ch: 'GU',

  // Historical / constructed
  la: 'VA',

  // China minorities
  bo: 'CN',
  ug: 'CN',
  za: 'CN',
  ii: 'CN',

  // South Asia extras
  dv: 'MV',
  ks: 'IN',
  sd: 'PK',
  sa: 'IN',
  pi: 'IN',

  fy: 'NL',

  // Caucasian
  os: 'RU',
  ce: 'RU',
  av: 'RU',
  ab: 'GE',

  // Turkic in Russia
  tt: 'RU',
  ba: 'RU',
  cv: 'RU',
  kv: 'RU',

  // Africa extras
  aa: 'ET',
  ak: 'GH',
  ee: 'GH',
  tw: 'GH',
  ln: 'CD',
  lu: 'CD',
  kg: 'CD',
  sg: 'CF',
  ki: 'KE',
  om: 'ET',
  kr: 'NE',
  kj: 'NA',
  hz: 'NA',
  ng: 'NA',
  nd: 'ZW',
  nr: 'ZA',
  ss: 'SZ',
  ts: 'ZA',
  ve: 'ZA',

  // Americas indigenous
  gn: 'PY',
  qu: 'PE',
  ay: 'BO',
  nv: 'US',
  oj: 'CA',
  cr: 'CA',
  iu: 'CA',
  ik: 'US',
  kl: 'GL',

  // Other European
  an: 'ES',
  wa: 'BE',
  li: 'NL',

  // Slavic historical
  cu: 'BG',
  mo: 'MD',

  yi: 'IL',
  bh: 'IN',
  ho: 'PG',
  sh: 'RS',

  // Romance
  oc: 'FR',
  co: 'FR',
  sc: 'IT',
  rm: 'CH',

  // Germanic
  gv: 'IM',
  kw: 'GB',

  // Uralic
  se: 'NO',
};

/**
 * Resolve a locale (`'en'`, `'pt-BR'`, `'zh_CN'`, …) to an ISO 3166-1 alpha-2
 * country code. Region suffixes win when present (`pt-BR` → `BR`).
 *
 * Returns `null` when no mapping exists — callers should render a graceful
 * fallback (no flag).
 */
export function getLanguageCountryCode(localeCode: string): TCountryCode | null {
  if (!localeCode) return null;
  const normalized = localeCode.replace('_', '-');

  // Region wins: pt-BR → BR, zh-CN → CN.
  const dash = normalized.indexOf('-');
  if (dash !== -1) {
    const region = normalized.slice(dash + 1).toUpperCase();
    if (region.length === 2) return region as TCountryCode;
  }

  const lang = normalized.slice(0, dash === -1 ? normalized.length : dash).toLowerCase() as TLanguageCode;
  return LANGUAGE_TO_COUNTRY[lang] ?? null;
}
