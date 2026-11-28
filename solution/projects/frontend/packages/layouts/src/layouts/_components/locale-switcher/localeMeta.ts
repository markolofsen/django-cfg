/**
 * Locale metadata — native name + english name per locale code.
 *
 * Covers the codes shipped with `@djangocfg/i18n` (and their common regional
 * variants). Unknown codes fall back to the uppercase code itself.
 */

export interface LocaleMeta {
  /** Native rendering — `'Русский'`, `'한국어'`. */
  native: string;
  /** English name — `'Russian'`, `'Korean'`. Used as the secondary line. */
  english: string;
  /** Marks the locale as RTL (`ar`, `he`, `fa`, `ur`). */
  rtl?: boolean;
}

const RTL_LANGS = new Set(['ar', 'he', 'fa', 'ur', 'ps', 'sd', 'yi', 'ku']);

const META: Record<string, { native: string; english: string }> = {
  // Major
  en: { native: 'English', english: 'English' },
  ru: { native: 'Русский', english: 'Russian' },
  ko: { native: '한국어', english: 'Korean' },
  zh: { native: '中文', english: 'Chinese' },
  ja: { native: '日本語', english: 'Japanese' },
  es: { native: 'Español', english: 'Spanish' },
  fr: { native: 'Français', english: 'French' },
  de: { native: 'Deutsch', english: 'German' },
  pt: { native: 'Português', english: 'Portuguese' },
  it: { native: 'Italiano', english: 'Italian' },
  ar: { native: 'العربية', english: 'Arabic' },
  hi: { native: 'हिन्दी', english: 'Hindi' },
  tr: { native: 'Türkçe', english: 'Turkish' },
  pl: { native: 'Polski', english: 'Polish' },
  nl: { native: 'Nederlands', english: 'Dutch' },
  uk: { native: 'Українська', english: 'Ukrainian' },

  // Regional variants
  'pt-BR': { native: 'Português (Brasil)', english: 'Portuguese (Brazil)' },
  'pt-PT': { native: 'Português (Portugal)', english: 'Portuguese (Portugal)' },
  'zh-CN': { native: '简体中文', english: 'Chinese (Simplified)' },
  'zh-TW': { native: '繁體中文', english: 'Chinese (Traditional)' },
  'en-US': { native: 'English (US)', english: 'English (US)' },
  'en-GB': { native: 'English (UK)', english: 'English (UK)' },
  'es-MX': { native: 'Español (México)', english: 'Spanish (Mexico)' },
  'es-ES': { native: 'Español (España)', english: 'Spanish (Spain)' },
  'fr-CA': { native: 'Français (Canada)', english: 'French (Canada)' },

  // Scandinavian
  sv: { native: 'Svenska', english: 'Swedish' },
  no: { native: 'Norsk', english: 'Norwegian' },
  nb: { native: 'Norsk Bokmål', english: 'Norwegian Bokmål' },
  nn: { native: 'Norsk Nynorsk', english: 'Norwegian Nynorsk' },
  da: { native: 'Dansk', english: 'Danish' },
  fi: { native: 'Suomi', english: 'Finnish' },
  is: { native: 'Íslenska', english: 'Icelandic' },

  // Other European
  cs: { native: 'Čeština', english: 'Czech' },
  sk: { native: 'Slovenčina', english: 'Slovak' },
  hu: { native: 'Magyar', english: 'Hungarian' },
  ro: { native: 'Română', english: 'Romanian' },
  bg: { native: 'Български', english: 'Bulgarian' },
  hr: { native: 'Hrvatski', english: 'Croatian' },
  sr: { native: 'Српски', english: 'Serbian' },
  sl: { native: 'Slovenščina', english: 'Slovenian' },
  et: { native: 'Eesti', english: 'Estonian' },
  lv: { native: 'Latviešu', english: 'Latvian' },
  lt: { native: 'Lietuvių', english: 'Lithuanian' },
  el: { native: 'Ελληνικά', english: 'Greek' },

  // Other
  th: { native: 'ไทย', english: 'Thai' },
  vi: { native: 'Tiếng Việt', english: 'Vietnamese' },
  id: { native: 'Indonesia', english: 'Indonesian' },
  ms: { native: 'Bahasa Melayu', english: 'Malay' },
  he: { native: 'עברית', english: 'Hebrew' },
  fa: { native: 'فارسی', english: 'Persian' },
};

function normalize(code: string): { exact: string; base: string } {
  const trimmed = code.trim();
  const dash = trimmed.indexOf('-');
  if (dash === -1) {
    return { exact: trimmed.toLowerCase(), base: trimmed.toLowerCase() };
  }
  const lang = trimmed.slice(0, dash).toLowerCase();
  const region = trimmed.slice(dash + 1).toUpperCase();
  return { exact: `${lang}-${region}`, base: lang };
}

export function getLocaleMeta(
  code: string,
  overrides?: Record<string, string>,
): LocaleMeta {
  const { exact, base } = normalize(code);

  // Manual overrides win — match either the exact code or the base.
  const overrideNative = overrides?.[code] ?? overrides?.[exact] ?? overrides?.[base];

  // Try exact match first (`pt-BR`), fall back to base (`pt`).
  const direct = META[exact] ?? META[base];

  return {
    native: overrideNative ?? direct?.native ?? code.toUpperCase(),
    english: direct?.english ?? code.toUpperCase(),
    rtl: RTL_LANGS.has(base),
  };
}
