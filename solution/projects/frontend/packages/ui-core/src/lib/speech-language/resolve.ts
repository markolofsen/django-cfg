import { WEB_SPEECH_LANGUAGES } from "./languages";

/**
 * The signals a default language is resolved from.
 *
 * Passed in rather than read from `navigator`/`localStorage` here: this is the
 * one rule in dictation worth testing exhaustively, and a function that reaches
 * for globals can only be tested by faking them.
 */
export interface LanguageSignals {
  /** What the user picked, if they ever did. Wins outright. */
  readonly picked?: string | undefined;
  /** The host UI's locale — an ISO subtag such as `ru`. A TIE-BREAKER only. */
  readonly uiLocale?: string | undefined;
  /** `navigator.languages`, in the browser's own order. */
  readonly browserLanguages?: readonly string[] | undefined;
  /** `navigator.language`. */
  readonly browserLanguage?: string | undefined;
  /** The runtime's `Intl` locale: the OS language/region, used only when no browser language is usable. */
  readonly intlLocale?: string | undefined;
}

const FALLBACK = "en-US";

/** ISO primary subtag → the catalogue's default dialect (`uk` → `uk-UA`). */
const ISO_TO_TAG: ReadonlyMap<string, string> = new Map(
  WEB_SPEECH_LANGUAGES.flatMap((language) => {
    const first = language.dialects[0];
    return first === undefined ? [] : [[language.iso.toLowerCase(), first.code] as const];
  }),
);

/** Every tag the catalogue knows, lowercased, for validating a candidate. */
const KNOWN_TAGS: ReadonlySet<string> = new Set(
  WEB_SPEECH_LANGUAGES.flatMap((language) =>
    language.dialects.map((dialect) => dialect.code.toLowerCase()),
  ),
);

/**
 * Primary subtags a browser or a UI locale spells differently from the catalogue:
 * `zh` is Chinese (the catalogue keys it `cmn`), `no`/`nn` are Norwegian (keyed `nb`).
 * Without this the 17 bundled UI locales left `zh` and `no` unresolved and dictation fell back to English.
 */
const ISO_ALIASES: Readonly<Record<string, string>> = { zh: "cmn", no: "nb", nn: "nb" };

/** Whole tags that name a catalogue dialect under another spelling (`zh-TW` is Mandarin in Traditional script). */
const TAG_ALIASES: Readonly<Record<string, string>> = {
  "zh-tw": "cmn-Hant-TW",
  "zh-hant": "cmn-Hant-TW",
  "zh-hant-tw": "cmn-Hant-TW",
  "zh-hk": "cmn-Hans-HK",
  "zh-cn": "cmn-Hans-CN",
  "zh-hans": "cmn-Hans-CN",
  "zh-hans-cn": "cmn-Hans-CN",
};

function isoOf(tag: string): string {
  const iso = tag.toLowerCase().split("-")[0] ?? "";
  return ISO_ALIASES[iso] ?? iso;
}

/**
 * Normalise anything language-shaped to a tag the Web Speech API accepts.
 *
 * A bare ISO subtag becomes the catalogue's default dialect for it; a full tag
 * is kept when the catalogue knows it, and otherwise falls back to that
 * language's default dialect. The last step is what rescues the measured case:
 * `en-ID` is a real browser value and not a speech tag, so it resolves to
 * `en-US` rather than being handed to an engine that will reject it.
 */
export function toSpeechTag(code: string | null | undefined): string | undefined {
  if (code === null || code === undefined) return undefined;
  const trimmed = code.trim();
  if (trimmed === "") return undefined;
  if (KNOWN_TAGS.has(trimmed.toLowerCase())) return trimmed;
  const aliased = TAG_ALIASES[trimmed.toLowerCase()];
  if (aliased !== undefined) return aliased;
  return ISO_TO_TAG.get(isoOf(trimmed));
}

/**
 * Which language dictation should listen for.
 *
 * Guessing for the user, in this order:
 *
 *   1. the user's explicit pick
 *   2. the UI locale, IF the browser also lists it as spoken
 *   3. the first language in `navigator.languages` that dictation supports
 *   4. `navigator.language`, then the `Intl` locale
 *   5. `en-US`
 *
 * The BROWSER decides, the app only breaks ties. A host that passes `ru` on a
 * browser that lists only English still gets English; a host that passes
 * nothing still gets the browser's language. Pinning speech to the app locale
 * is a known regression — an English UI then cannot dictate Russian.
 *
 * Rung 2 exists because of a measured failure: `navigator.language` was `en-ID`
 * while `navigator.languages` contained `ru` and the app was set to Russian.
 * Rung 3 walks the whole list rather than trusting position one: the first
 * entry may be a language dictation has no engine for (`xx`), and the second is
 * then the real answer.
 */
export function resolveLanguage(signals: LanguageSignals): string {
  const picked = toSpeechTag(signals.picked);
  if (picked !== undefined) return picked;

  const list = signals.browserLanguages ?? [];
  const uiIso = isoOf(signals.uiLocale ?? "");
  if (uiIso !== "" && list.map(isoOf).includes(uiIso)) {
    const tag = ISO_TO_TAG.get(uiIso);
    if (tag !== undefined) return tag;
  }

  for (const candidate of list) {
    const tag = toSpeechTag(candidate);
    if (tag !== undefined) return tag;
  }

  return toSpeechTag(signals.browserLanguage) ?? toSpeechTag(signals.intlLocale) ?? FALLBACK;
}

/**
 * The browser's languages as speech tags, best first, one per language: the
 * candidate set a picker shows ahead of the full catalogue (a user whose browser
 * UI is Indonesian usually still lists Russian or English right after it).
 */
export function browserSpeechTags(languages: readonly string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const code of languages) {
    const tag = toSpeechTag(code);
    if (tag === undefined) continue;
    const iso = isoOf(tag);
    if (seen.has(iso)) continue;
    seen.add(iso);
    out.push(tag);
  }
  return out;
}
