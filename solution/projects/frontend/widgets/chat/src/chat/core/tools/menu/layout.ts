// Keyboard-layout transliteration for search input.
//
// May import: nothing.

/**
 * QWERTY→ЙЦУКЕН by physical key. The pair is positional, not phonetic: `g`
 * and `п` are the same key, so someone who meant "generate" and left the
 * layout on Russian produces "пуньфеу".
 */
const RU_BY_KEY = "йцукенгшщзхъфывапролджэячсмитьбю.ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ,Ё";
const EN_BY_KEY = "qwertyuiop[]asdfghjkl;'zxcvbnm,./`QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?~";

const TO_EN = new Map<string, string>();
const TO_RU = new Map<string, string>();
for (const [index, ru] of [...RU_BY_KEY].entries()) {
  const en = EN_BY_KEY[index];
  if (en === undefined) continue;
  TO_EN.set(ru, en);
  TO_RU.set(en, ru);
}

function transliterate(value: string, table: ReadonlyMap<string, string>): string {
  let out = "";
  for (const char of value) out += table.get(char) ?? char;
  return out;
}

/**
 * What was typed, plus each layout reading of it.
 *
 * Both directions: the mistake runs either way, and guessing which costs a
 * keystroke. The original comes first, so a caller can rank an exact hit above
 * a transliterated one.
 */
export function queryLayoutForms(query: string): readonly string[] {
  const typed = query.trim();
  if (typed === "") return [];

  const forms = [typed];
  for (const candidate of [transliterate(typed, TO_EN), transliterate(typed, TO_RU)]) {
    if (candidate !== typed && !forms.includes(candidate)) forms.push(candidate);
  }
  return forms;
}
