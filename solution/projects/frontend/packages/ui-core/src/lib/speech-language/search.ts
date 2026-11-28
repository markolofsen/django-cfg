/**
 * Layout-independent language search.
 *
 * Typing "he,bq" on an EN layout while thinking «русый», or "hecc" for
 * «русс», is the single most common way a bilingual user searches a
 * language list — the physical keys are right, the layout is wrong.
 * Every query is therefore expanded through the QWERTY↔ЙЦУКЕН key maps
 * and EVERY variant is matched, so «рус», "rus", "russian" and "hec"
 * (=рус on EN keys) all find Русский.
 *
 * The maps cover the RU↔EN pair only — the pair our users actually mix.
 * The mechanism is additive: more layout pairs can be appended to
 * `LAYOUT_PAIRS` without touching the matcher.
 */

/** QWERTY key → ЙЦУКЕН character on the same physical key. */
const EN_TO_RU: Record<string, string> = {
  q: 'й', w: 'ц', e: 'у', r: 'к', t: 'е', y: 'н', u: 'г', i: 'ш', o: 'щ',
  p: 'з', '[': 'х', ']': 'ъ', a: 'ф', s: 'ы', d: 'в', f: 'а', g: 'п',
  h: 'р', j: 'о', k: 'л', l: 'д', ';': 'ж', "'": 'э', z: 'я', x: 'ч',
  c: 'с', v: 'м', b: 'и', n: 'т', m: 'ь', ',': 'б', '.': 'ю',
};

/** ЙЦУКЕН character → QWERTY key on the same physical key. */
const RU_TO_EN: Record<string, string> = Object.fromEntries(
  Object.entries(EN_TO_RU).map(([en, ru]) => [ru, en]),
);

const LAYOUT_PAIRS: Record<string, string>[] = [EN_TO_RU, RU_TO_EN];

function remap(query: string, table: Record<string, string>): string {
  let out = '';
  for (const ch of query) out += table[ch] ?? ch;
  return out;
}

/**
 * All layout interpretations of a raw query, lowercased and de-duplicated.
 * Always includes the query itself.
 */
export function expandQueryLayouts(query: string): string[] {
  const q = query.trim().toLowerCase();
  if (!q) return [];
  const variants = new Set<string>([q]);
  for (const table of LAYOUT_PAIRS) {
    const mapped = remap(q, table);
    if (mapped !== q) variants.add(mapped);
  }
  return [...variants];
}

/**
 * True when ANY layout variant of `query` is a substring of `haystack`.
 * `haystack` must already be lowercase (build it once per row —
 * `SpeechLanguageRow.search` packs native name, English name, ISO, tag
 * and region).
 */
export function matchesLanguageQuery(haystack: string, query: string): boolean {
  const variants = expandQueryLayouts(query);
  if (variants.length === 0) return true;
  return variants.some((v) => haystack.includes(v));
}
