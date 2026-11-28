import { join } from "node:path";
import { checkDictionaries } from "@djangocfg/i18n/copy/testing";
import { describe, expect, it } from "vitest";

import { CHAT_DICTIONARIES, plural } from "./index";
import { en } from "./locales/en";
import type { ChatCopy, PluralCopy } from "./types";

/**
 * What `tsc` cannot check about the dictionaries.
 *
 * The schema makes every dictionary complete and correctly spelled. It cannot
 * see whether a dictionary was written and then never REGISTERED — the file
 * typechecks, the locale loads English, and no error is raised anywhere.
 */

describe("chat dictionaries", () => {
  it("covers every locale, every file, every key and placeholder", () => {
    expect(checkDictionaries(CHAT_DICTIONARIES, join(import.meta.dirname, "locales"))).toEqual([]);
  });

  it("resolves pt-BR to Portuguese, not English", () => {
    // MUTANT: write the key as `ptBR` in the registry → this dies while every
    // other test stays green, which is exactly the failure mode.
    expect(CHAT_DICTIONARIES["pt-BR"]?.composer.send).toBe("Enviar");
    expect(CHAT_DICTIONARIES["pt-BR"]?.composer.send).not.toBe(en.composer.send);
  });

  it("gives every dictionary the plural categories its language selects", () => {
    // The type requires `other` and permits the rest. What it cannot say is
    // that a language which SELECTS `few` has one written — English falling
    // back is correct, a Russian dictionary missing `many` is not.
    const missing: string[] = [];

    for (const [language, copy] of Object.entries(CHAT_DICTIONARIES)) {
      const rules = new Intl.PluralRules(language);
      const needed = new Set(
        // Enough counts to reach every category any of these languages uses:
        // 0 and 1 (zero/one), 2 (two), 3 (few), 5/11 (many), 1.5 (other).
        [0, 1, 2, 3, 5, 11, 21, 1.5].map((n) => rules.select(n)),
      );

      const plurals: readonly [string, PluralCopy][] = [
        ["queue.prompts", copy.queue.prompts],
      ];

      for (const [name, forms] of plurals) {
        for (const category of needed) {
          // `Intl.LDMLPluralRule` and `PluralCopy`'s keys are the same six
          // names, which is what makes this index safe — and what makes the
          // schema's optional fields the right shape.
          if (forms[category] === undefined) missing.push(`${language} ${name}.${category}`);
        }
      }
    }

    expect(missing).toEqual([]);
  });

  it("interpolates the count into the form the language selects", () => {
    const ru = CHAT_DICTIONARIES["ru"] as ChatCopy;

    // Russian is the case that motivated `Intl.PluralRules` over a two-form
    // ternary: 1 / 3 / 5 take three different endings, and 21 returns to the
    // first — which a `count === 1` check gets wrong.
    expect(plural(ru.queue.prompts, 1, "ru")).toBe("1 сообщение в очереди");
    expect(plural(ru.queue.prompts, 3, "ru")).toBe("3 сообщения в очереди");
    expect(plural(ru.queue.prompts, 5, "ru")).toBe("5 сообщений в очереди");
    expect(plural(ru.queue.prompts, 21, "ru")).toBe("21 сообщение в очереди");
  });

  it("falls back to other rather than rendering nothing", () => {
    // A language whose category is absent from the dictionary: English strings
    // resolved for an untranslated locale still meet Russian's `many`. Wrong
    // wording beats an empty label on a control the user is reading.
    expect(plural(en.queue.prompts, 5, "ru")).toBe("5 prompts queued");
  });

  it("survives a language tag Intl cannot parse", () => {
    // MUTANT: drop the try/catch in `rulesFor` → this throws. A malformed tag
    // must not take the composer down; the words stay readable.
    expect(plural(en.queue.prompts, 2, "not a language")).toBe("2 prompts queued");
  });
});
