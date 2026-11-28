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
import type { ChatCopy } from "./types";

export type {
  ChatCopy,
  ComposerCopy,
  MessageCopy,
  PluralCopy,
  QueueCopy,
  RoomCopy,
  RunCopy,
  ToolCopy,
  TranscriptCopy,
  VoiceCopy,
} from "./types";
export { fill, plural } from "@djangocfg/i18n/copy";
export { roomMentionItems, type RoomMentionItem } from "./room";

/** Every bundled dictionary, typed complete over the shared `Locale` union. */
export const CHAT_DICTIONARIES: Readonly<Record<Locale, ChatCopy>> = {
  en, ru, ko, ja, de, fr, zh, it, es, nl, ar, tr, pl, sv, no, da,
  // The key is `pt-BR`, which is not a valid JS identifier, so the binding is `ptBR`.
  "pt-BR": ptBR,
};

const kit = createCopy(CHAT_DICTIONARIES);

/**
 * The chat dictionary for the active language: the `locale` prop, else the
 * `@djangocfg/i18n` provider, else English. The package owns its copy rather
 * than taking labels as props, because a host assembling a translated string
 * into a DOM selector once broke the composer caret in a single locale.
 */
export const useChatCopy = kit.useCopy;

/** The room words (`@` menu, recipient chip, link copy) for the active language: the `room` section of the chat dictionary. */
export function useRoomCopy(): ChatCopy["room"] {
  return useChatCopy().room;
}

/** The bundled locale in use, for `plural()`; a plural category is needed on every render. */
export const useChatLanguage = kit.useLocale;
