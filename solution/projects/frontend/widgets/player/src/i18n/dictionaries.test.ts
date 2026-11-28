import { join } from "node:path";
import { checkDictionaries } from "@djangocfg/i18n/copy/testing";
import { describe, expect, it } from "vitest";

import { PLAYER_DICTIONARIES, fill } from "./index";
import { en } from "./locales/en";

/**
 * What `tsc` cannot check about the dictionaries.
 *
 * The schema makes every dictionary complete and correctly spelled. It cannot
 * see whether a dictionary was written and then never REGISTERED — the file
 * typechecks, the locale loads English, and no error is raised anywhere.
 */

describe("player dictionaries", () => {
  it("covers every locale, every file, every key and placeholder", () => {
    expect(checkDictionaries(PLAYER_DICTIONARIES, join(import.meta.dirname, "locales"))).toEqual([]);
  });

  it("resolves pt-BR to Portuguese, not English", () => {
    // MUTANT: write the key as `ptBR` in the registry → this dies while every
    // other test stays green, which is exactly the failure mode.
    expect(PLAYER_DICTIONARIES["pt-BR"]?.transport.play).toBe("Reproduzir");
    expect(PLAYER_DICTIONARIES["pt-BR"]?.transport.play).not.toBe(en.transport.play);
  });

  it("keeps the machine placeholder in every locale that names a machine", () => {
    // A translator can drop `{{machine}}` and leave a sentence that still reads
    // fine — and then the one fact the string exists to carry is gone. The
    // unnamed variant is the deliberate counterpart and must NOT carry one.
    const missing: string[] = [];
    for (const [language, copy] of Object.entries(PLAYER_DICTIONARIES)) {
      if (!copy.failure.machineUnreachable.includes("{{machine}}")) {
        missing.push(`${language} machineUnreachable`);
      }
      if (copy.failure.machineUnreachableUnnamed.includes("{{machine}}")) {
        missing.push(`${language} machineUnreachableUnnamed has a placeholder`);
      }
    }
    expect(missing).toEqual([]);
  });

  it("substitutes the machine name", () => {
    expect(fill(en.failure.machineUnreachable, { machine: "server" })).toBe(
      "server went offline — playback stopped",
    );
  });

  it("leaves an unknown placeholder intact rather than emptying it", () => {
    // A missing value must not silently delete the placeholder: a visible
    // `{{machine}}` is a bug someone reports, an empty gap is one nobody sees.
    expect(fill("a {{missing}} b", {})).toBe("a {{missing}} b");
  });
});
