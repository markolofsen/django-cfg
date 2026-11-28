/**
 * Canonical list of BCP-47 language tags that the browser Web Speech
 * API is known to accept. Sourced from the official Google Chrome
 * Speech API demo (`google.com/intl/en/chrome/demos/speech.html`),
 * which is the de-facto reference — the spec itself doesn't expose a
 * way to enumerate supported languages, so this list is the
 * best-effort guarantee for what works in Chromium-based browsers.
 *
 * Each entry groups one human-readable language with its dialect
 * variants. The default tag (first in `dialects`) is what `lang` is
 * set to when the user picks the language without a regional dialect.
 *
 * A host whose engine is not the browser can narrow this list — a server
 * transcriber may accept more or fewer tags than Web Speech does.
 */

export interface SpeechLanguageDialect {
  /** BCP-47 tag (e.g. `en-US`). */
  code: string;
  /** Region label in the language's native script (e.g. "United States"). */
  region: string;
}

export interface SpeechLanguage {
  /** Native-script name (e.g. "Русский", "中文"). */
  name: string;
  /**
   * English name used as a secondary search key so users typing
   * "russian" / "chinese" / "korean" land on the right row regardless
   * of the native script. Always lowercase.
   */
  englishName: string;
  /**
   * Primary-subtag ISO-639 code (e.g. `en`, `ru`, `cmn`). The key a UI locale
   * is matched against when resolving a default.
   */
  iso: string;
  /** One or more region dialects. Length >= 1. */
  dialects: SpeechLanguageDialect[];
}

export const WEB_SPEECH_LANGUAGES: SpeechLanguage[] = [
  { name: 'Afrikaans', iso: 'af', englishName: 'afrikaans', dialects: [{ code: 'af-ZA', region: 'South Africa' }] },
  { name: 'አማርኛ', iso: 'am', englishName: 'amharic', dialects: [{ code: 'am-ET', region: 'Ethiopia' }] },
  { name: 'Azərbaycanca', iso: 'az', englishName: 'azerbaijani', dialects: [{ code: 'az-AZ', region: 'Azerbaijan' }] },
  {
    name: 'বাংলা', iso: 'bn', englishName: 'bengali',
    dialects: [
      { code: 'bn-BD', region: 'Bangladesh' },
      { code: 'bn-IN', region: 'India' },
    ],
  },
  { name: 'Bahasa Indonesia', iso: 'id', englishName: 'indonesian', dialects: [{ code: 'id-ID', region: 'Indonesia' }] },
  { name: 'Bahasa Melayu', iso: 'ms', englishName: 'malay', dialects: [{ code: 'ms-MY', region: 'Malaysia' }] },
  { name: 'Català', iso: 'ca', englishName: 'catalan', dialects: [{ code: 'ca-ES', region: 'Spain' }] },
  { name: 'Čeština', iso: 'cs', englishName: 'czech', dialects: [{ code: 'cs-CZ', region: 'Czechia' }] },
  { name: 'Dansk', iso: 'da', englishName: 'danish', dialects: [{ code: 'da-DK', region: 'Denmark' }] },
  { name: 'Deutsch', iso: 'de', englishName: 'german', dialects: [{ code: 'de-DE', region: 'Germany' }] },
  {
    name: 'English', iso: 'en', englishName: 'english',
    dialects: [
      { code: 'en-US', region: 'United States' },
      { code: 'en-GB', region: 'United Kingdom' },
      { code: 'en-AU', region: 'Australia' },
      { code: 'en-CA', region: 'Canada' },
      { code: 'en-IN', region: 'India' },
      { code: 'en-NZ', region: 'New Zealand' },
      { code: 'en-PH', region: 'Philippines' },
      { code: 'en-ZA', region: 'South Africa' },
      { code: 'en-NG', region: 'Nigeria' },
      { code: 'en-GH', region: 'Ghana' },
      { code: 'en-KE', region: 'Kenya' },
      { code: 'en-TZ', region: 'Tanzania' },
    ],
  },
  {
    name: 'Español', iso: 'es', englishName: 'spanish',
    dialects: [
      { code: 'es-ES', region: 'España' },
      { code: 'es-MX', region: 'México' },
      { code: 'es-US', region: 'Estados Unidos' },
      { code: 'es-AR', region: 'Argentina' },
      { code: 'es-CL', region: 'Chile' },
      { code: 'es-CO', region: 'Colombia' },
      { code: 'es-PE', region: 'Perú' },
      { code: 'es-VE', region: 'Venezuela' },
      { code: 'es-EC', region: 'Ecuador' },
      { code: 'es-GT', region: 'Guatemala' },
      { code: 'es-CR', region: 'Costa Rica' },
      { code: 'es-PA', region: 'Panamá' },
      { code: 'es-DO', region: 'Rep. Dominicana' },
      { code: 'es-UY', region: 'Uruguay' },
      { code: 'es-PY', region: 'Paraguay' },
      { code: 'es-BO', region: 'Bolivia' },
      { code: 'es-SV', region: 'El Salvador' },
      { code: 'es-HN', region: 'Honduras' },
      { code: 'es-NI', region: 'Nicaragua' },
      { code: 'es-PR', region: 'Puerto Rico' },
    ],
  },
  { name: 'Euskara', iso: 'eu', englishName: 'basque', dialects: [{ code: 'eu-ES', region: 'Spain' }] },
  { name: 'Filipino', iso: 'fil', englishName: 'filipino tagalog', dialects: [{ code: 'fil-PH', region: 'Philippines' }] },
  { name: 'Français', iso: 'fr', englishName: 'french', dialects: [{ code: 'fr-FR', region: 'France' }] },
  { name: 'Basa Jawa', iso: 'jv', englishName: 'javanese', dialects: [{ code: 'jv-ID', region: 'Indonesia' }] },
  { name: 'Galego', iso: 'gl', englishName: 'galician', dialects: [{ code: 'gl-ES', region: 'Spain' }] },
  { name: 'ગુજરાતી', iso: 'gu', englishName: 'gujarati', dialects: [{ code: 'gu-IN', region: 'India' }] },
  { name: 'Hrvatski', iso: 'hr', englishName: 'croatian', dialects: [{ code: 'hr-HR', region: 'Croatia' }] },
  { name: 'IsiZulu', iso: 'zu', englishName: 'zulu', dialects: [{ code: 'zu-ZA', region: 'South Africa' }] },
  { name: 'Íslenska', iso: 'is', englishName: 'icelandic', dialects: [{ code: 'is-IS', region: 'Iceland' }] },
  {
    name: 'Italiano', iso: 'it', englishName: 'italian',
    dialects: [
      { code: 'it-IT', region: 'Italia' },
      { code: 'it-CH', region: 'Svizzera' },
    ],
  },
  { name: 'ಕನ್ನಡ', iso: 'kn', englishName: 'kannada', dialects: [{ code: 'kn-IN', region: 'India' }] },
  { name: 'ភាសាខ្មែរ', iso: 'km', englishName: 'khmer cambodian', dialects: [{ code: 'km-KH', region: 'Cambodia' }] },
  { name: 'Latviešu', iso: 'lv', englishName: 'latvian', dialects: [{ code: 'lv-LV', region: 'Latvia' }] },
  { name: 'Lietuvių', iso: 'lt', englishName: 'lithuanian', dialects: [{ code: 'lt-LT', region: 'Lithuania' }] },
  { name: 'മലയാളം', iso: 'ml', englishName: 'malayalam', dialects: [{ code: 'ml-IN', region: 'India' }] },
  { name: 'मराठी', iso: 'mr', englishName: 'marathi', dialects: [{ code: 'mr-IN', region: 'India' }] },
  { name: 'Magyar', iso: 'hu', englishName: 'hungarian', dialects: [{ code: 'hu-HU', region: 'Hungary' }] },
  { name: 'ລາວ', iso: 'lo', englishName: 'lao laotian', dialects: [{ code: 'lo-LA', region: 'Laos' }] },
  { name: 'Nederlands', iso: 'nl', englishName: 'dutch', dialects: [{ code: 'nl-NL', region: 'Netherlands' }] },
  { name: 'नेपाली भाषा', iso: 'ne', englishName: 'nepali', dialects: [{ code: 'ne-NP', region: 'Nepal' }] },
  { name: 'Norsk bokmål', iso: 'nb', englishName: 'norwegian bokmal', dialects: [{ code: 'nb-NO', region: 'Norway' }] },
  { name: 'Polski', iso: 'pl', englishName: 'polish', dialects: [{ code: 'pl-PL', region: 'Poland' }] },
  {
    name: 'Português', iso: 'pt', englishName: 'portuguese',
    dialects: [
      { code: 'pt-BR', region: 'Brasil' },
      { code: 'pt-PT', region: 'Portugal' },
    ],
  },
  { name: 'Română', iso: 'ro', englishName: 'romanian', dialects: [{ code: 'ro-RO', region: 'Romania' }] },
  { name: 'සිංහල', iso: 'si', englishName: 'sinhala sinhalese', dialects: [{ code: 'si-LK', region: 'Sri Lanka' }] },
  { name: 'Slovenščina', iso: 'sl', englishName: 'slovenian', dialects: [{ code: 'sl-SI', region: 'Slovenia' }] },
  { name: 'Basa Sunda', iso: 'su', englishName: 'sundanese', dialects: [{ code: 'su-ID', region: 'Indonesia' }] },
  { name: 'Slovenčina', iso: 'sk', englishName: 'slovak', dialects: [{ code: 'sk-SK', region: 'Slovakia' }] },
  { name: 'Suomi', iso: 'fi', englishName: 'finnish', dialects: [{ code: 'fi-FI', region: 'Finland' }] },
  { name: 'Svenska', iso: 'sv', englishName: 'swedish', dialects: [{ code: 'sv-SE', region: 'Sweden' }] },
  {
    name: 'Kiswahili', iso: 'sw', englishName: 'swahili',
    dialects: [
      { code: 'sw-TZ', region: 'Tanzania' },
      { code: 'sw-KE', region: 'Kenya' },
    ],
  },
  { name: 'ქართული', iso: 'ka', englishName: 'georgian', dialects: [{ code: 'ka-GE', region: 'Georgia' }] },
  { name: 'Հայերեն', iso: 'hy', englishName: 'armenian', dialects: [{ code: 'hy-AM', region: 'Armenia' }] },
  {
    name: 'தமிழ்', iso: 'ta', englishName: 'tamil',
    dialects: [
      { code: 'ta-IN', region: 'இந்தியா' },
      { code: 'ta-SG', region: 'சிங்கப்பூர்' },
      { code: 'ta-LK', region: 'இலங்கை' },
      { code: 'ta-MY', region: 'மலேசியா' },
    ],
  },
  { name: 'తెలుగు', iso: 'te', englishName: 'telugu', dialects: [{ code: 'te-IN', region: 'India' }] },
  { name: 'Tiếng Việt', iso: 'vi', englishName: 'vietnamese', dialects: [{ code: 'vi-VN', region: 'Vietnam' }] },
  { name: 'Türkçe', iso: 'tr', englishName: 'turkish', dialects: [{ code: 'tr-TR', region: 'Türkiye' }] },
  {
    name: 'اُردُو', iso: 'ur', englishName: 'urdu',
    dialects: [
      { code: 'ur-PK', region: 'پاکستان' },
      { code: 'ur-IN', region: 'بھارت' },
    ],
  },
  { name: 'Ελληνικά', iso: 'el', englishName: 'greek', dialects: [{ code: 'el-GR', region: 'Greece' }] },
  { name: 'български', iso: 'bg', englishName: 'bulgarian', dialects: [{ code: 'bg-BG', region: 'Bulgaria' }] },
  { name: 'Русский', iso: 'ru', englishName: 'russian', dialects: [{ code: 'ru-RU', region: 'Russia' }] },
  { name: 'Српски', iso: 'sr', englishName: 'serbian', dialects: [{ code: 'sr-RS', region: 'Serbia' }] },
  { name: 'Українська', iso: 'uk', englishName: 'ukrainian', dialects: [{ code: 'uk-UA', region: 'Ukraine' }] },
  { name: '한국어', iso: 'ko', englishName: 'korean', dialects: [{ code: 'ko-KR', region: 'Korea' }] },
  {
    name: '中文', iso: 'cmn', englishName: 'chinese mandarin cantonese',
    dialects: [
      { code: 'cmn-Hans-CN', region: '普通话 (中国大陆)' },
      { code: 'cmn-Hans-HK', region: '普通话 (香港)' },
      { code: 'cmn-Hant-TW', region: '中文 (台灣)' },
      { code: 'yue-Hant-HK', region: '粵語 (香港)' },
    ],
  },
  { name: '日本語', iso: 'ja', englishName: 'japanese', dialects: [{ code: 'ja-JP', region: 'Japan' }] },
  { name: 'हिन्दी', iso: 'hi', englishName: 'hindi', dialects: [{ code: 'hi-IN', region: 'India' }] },
  { name: 'ภาษาไทย', iso: 'th', englishName: 'thai', dialects: [{ code: 'th-TH', region: 'Thailand' }] },
  {
    name: 'العربية', iso: 'ar', englishName: 'arabic',
    dialects: [
      { code: 'ar-SA', region: 'المملكة العربية السعودية' },
      { code: 'ar-EG', region: 'مصر' },
      { code: 'ar-AE', region: 'الإمارات' },
      { code: 'ar-MA', region: 'المغرب' },
      { code: 'ar-DZ', region: 'الجزائر' },
      { code: 'ar-JO', region: 'الأردن' },
      { code: 'ar-IQ', region: 'العراق' },
      { code: 'ar-KW', region: 'الكويت' },
      { code: 'ar-LB', region: 'لبنان' },
      { code: 'ar-QA', region: 'قطر' },
      { code: 'ar-TN', region: 'تونس' },
    ],
  },
];

/** Flat list of every supported BCP-47 tag, useful for validation. */
export const WEB_SPEECH_TAGS: string[] = WEB_SPEECH_LANGUAGES.flatMap((l) =>
  l.dialects.map((d) => d.code),
);

/**
 * Find the human-readable language entry that owns a given BCP-47 tag.
 * Returns `null` for unknown / custom tags (custom engines may use
 * codes outside this catalogue).
 */
export function findSpeechLanguage(tag: string | null | undefined): {
  language: SpeechLanguage;
  dialect: SpeechLanguageDialect;
} | null {
  if (!tag) return null;
  const lower = tag.toLowerCase();
  for (const language of WEB_SPEECH_LANGUAGES) {
    for (const dialect of language.dialects) {
      if (dialect.code.toLowerCase() === lower) return { language, dialect };
    }
  }
  return null;
}

/**
 * Extract the ISO-3166 country code (2 uppercase letters) from a
 * BCP-47 tag, or `null` if the tag has no region subtag. Used by the
 * language flag button to find the right country flag asset.
 */
export function countryFromTag(tag: string | null | undefined): string | null {
  if (!tag) return null;
  const parts = tag.split('-');
  for (let i = parts.length - 1; i >= 0; i -= 1) {
    const p = parts[i];
    if (p && p.length === 2 && /^[A-Za-z]{2}$/.test(p)) return p.toUpperCase();
  }
  return null;
}

export interface SpeechLanguageRow {
  /** BCP-47 tag (e.g. `ru-RU`). */
  tag: string;
  /** Display label: native name, plus region when the language has >1 dialect. */
  label: string;
  /** ISO-3166 country for the flag asset, or null for region-less tags. */
  country: string | null;
  /**
   * Lowercased search haystack: native name + English name + ISO + tag
   * + region. Match with `matchesLanguageQuery` (layout-independent).
   */
  search: string;
}

/**
 * Flatten the catalogue into ready-to-render menu rows — the single
 * builder behind every language list surface (`VoiceControlMenu`
 * submenu, the in-recording `LanguageChip` dropdown). `allowedTags`
 * narrows the list for backend engines that support a subset.
 */
export function buildLanguageRows(allowedTags?: string[]): SpeechLanguageRow[] {
  const allow = allowedTags ? new Set(allowedTags) : null;
  const rows: SpeechLanguageRow[] = [];
  for (const lang of WEB_SPEECH_LANGUAGES) {
    for (const d of lang.dialects) {
      if (allow && !allow.has(d.code)) continue;
      rows.push({
        tag: d.code,
        label:
          lang.dialects.length === 1 ? lang.name : `${lang.name} — ${d.region}`,
        country: countryFromTag(d.code),
        search:
          `${lang.name} ${lang.englishName} ${lang.iso} ${d.code} ${d.region}`.toLowerCase(),
      });
    }
  }
  return rows;
}
