export {
  WEB_SPEECH_LANGUAGES,
  WEB_SPEECH_TAGS,
  findSpeechLanguage,
  countryFromTag,
  buildLanguageRows,
} from "./languages";
export type { SpeechLanguage, SpeechLanguageDialect, SpeechLanguageRow } from "./languages";
export { expandQueryLayouts, matchesLanguageQuery } from "./search";
export { resolveLanguage, toSpeechTag, browserSpeechTags } from "./resolve";
export type { LanguageSignals } from "./resolve";
export { useSpeechLanguage } from "./useSpeechLanguage";
export type { UseSpeechLanguageResult, SpeechLanguageOptions } from "./useSpeechLanguage";
