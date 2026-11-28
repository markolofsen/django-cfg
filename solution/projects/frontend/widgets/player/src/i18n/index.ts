import { createCopy, type Locale } from "@djangocfg/i18n/copy";

import { ar } from "./locales/ar";
import { da } from "./locales/da";
import { de } from "./locales/de";
import { en } from "./locales/en";
import { es } from "./locales/es";
import { fr } from "./locales/fr";
import { it } from "./locales/it";
import { ja } from "./locales/ja";
import { ko } from "./locales/ko";
import { nl } from "./locales/nl";
import { no } from "./locales/no";
import { pl } from "./locales/pl";
import { ptBR } from "./locales/ptBR";
import { ru } from "./locales/ru";
import { sv } from "./locales/sv";
import { tr } from "./locales/tr";
import { zh } from "./locales/zh";
import type { PlayerCopy } from "./types";

export type {
  ControlsCopy,
  DockCopy,
  FailureCopy,
  InfoCopy,
  PlayerCopy,
  StageCopy,
  TransportCopy,
} from "./types";

/** Every bundled dictionary, typed complete over the shared `Locale` union. */
export const PLAYER_DICTIONARIES: Readonly<Record<Locale, PlayerCopy>> = {
  en, ru, ko, ja, de, fr, zh, it, es, nl, ar, tr, pl, sv, no, da,
  // The key is `pt-BR`, which is not a valid JS identifier, so the binding is `ptBR`.
  "pt-BR": ptBR,
};

const kit = createCopy(PLAYER_DICTIONARIES);

/**
 * The player dictionary for the active language: the `locale` prop, else the
 * `@djangocfg/i18n` provider, else English. Typed as a whole object, not a
 * `t(key)` resolver, so a missing key is a `tsc` error rather than a runtime miss.
 */
export const usePlayerCopy = kit.useCopy;

/** Substitute `{name}` placeholders; the placeholder belongs to the catalogue, so a translator can move it. */
export { fill } from "@djangocfg/i18n/copy";
