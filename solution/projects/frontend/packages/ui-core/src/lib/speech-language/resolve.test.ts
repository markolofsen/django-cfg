import { describe, expect, it } from "vitest";

import { resolveLanguage, toSpeechTag } from "./resolve";

describe("toSpeechTag", () => {
  it("keeps a tag the catalogue knows", () => {
    expect(toSpeechTag("ru-RU")).toBe("ru-RU");
    expect(toSpeechTag("en-GB")).toBe("en-GB");
  });

  it("expands a bare ISO subtag to that language's default dialect", () => {
    expect(toSpeechTag("ru")).toBe("ru-RU");
    // The case a naive `<code>-<UPPER(code)>` rule gets wrong: `uk-UK` is not a
    // real tag, and an engine handed it fails rather than falling back.
    expect(toSpeechTag("uk")).toBe("uk-UA");
  });

  it("repairs a real browser tag that is not a speech tag", () => {
    // `en-ID` is what the measured browser reported. It is a legitimate locale
    // and not something Web Speech accepts.
    expect(toSpeechTag("en-ID")).toBe("en-US");
  });

  it("maps the UI locales the catalogue spells differently: zh and no", () => {
    expect(toSpeechTag("zh")).toBe("cmn-Hans-CN");
    expect(toSpeechTag("zh-TW")).toBe("cmn-Hant-TW");
    expect(toSpeechTag("no")).toBe("nb-NO");
    expect(toSpeechTag("ar")).toBe("ar-SA");
    expect(resolveLanguage({ uiLocale: "zh", browserLanguages: ["en-US", "zh-CN"], browserLanguage: "en-US" })).toBe("cmn-Hans-CN");
  });

  it("returns undefined for nothing, so a caller can fall through", () => {
    expect(toSpeechTag(undefined)).toBeUndefined();
    expect(toSpeechTag(null)).toBeUndefined();
    expect(toSpeechTag("   ")).toBeUndefined();
    expect(toSpeechTag("zzz")).toBeUndefined();
  });
});

describe("resolveLanguage", () => {
  it("prefers the explicit pick over every other signal", () => {
    expect(
      resolveLanguage({
        picked: "de-DE",
        uiLocale: "ru",
        browserLanguages: ["ru-RU", "ru"],
        browserLanguage: "ru-RU",
      }),
    ).toBe("de-DE");
  });

  it("resolves the measured app case to Russian", () => {
    // navigator.language was `en-ID` while `navigator.languages` listed `ru`
    // and the app locale was `ru`. Reading position one alone gave English
    // and left dictation deaf to the language being spoken.
    expect(
      resolveLanguage({
        uiLocale: "ru",
        browserLanguages: ["en-ID", "ru-ID", "ru", "en", "id"],
        browserLanguage: "en-ID",
      }),
    ).toBe("ru-RU");
  });

  it("refuses to follow the UI locale the browser does not list as spoken", () => {
    // THE guard against the known regression: pinning speech to the app locale
    // makes an English UI unable to dictate Russian. A Russian UI on a browser
    // that lists only English must still dictate English.
    expect(
      resolveLanguage({
        uiLocale: "ru",
        browserLanguages: ["en-US", "en"],
        browserLanguage: "en-US",
      }),
    ).toBe("en-US");
  });

  it("falls back to navigator.language when the UI locale breaks no tie", () => {
    expect(
      resolveLanguage({
        uiLocale: "en",
        browserLanguages: ["de-DE", "de"],
        browserLanguage: "de-DE",
      }),
    ).toBe("de-DE");
  });

  it("falls back to en-US when nothing is known", () => {
    expect(resolveLanguage({})).toBe("en-US");
  });

  it("does not let an unknown UI locale reach the engine", () => {
    // `xx` is listed as spoken by a hostile or exotic browser, but the
    // catalogue has no tag for it; falling through beats emitting `xx-XX`.
    expect(
      resolveLanguage({
        uiLocale: "xx",
        browserLanguages: ["xx", "de-DE"],
        browserLanguage: "de-DE",
      }),
    ).toBe("de-DE");
  });
});

describe("resolveLanguage: guessing from the browser", () => {
  it("takes the browser's language when the host passes no locale", () => {
    expect(resolveLanguage({ browserLanguages: ["ru-RU", "en-US"], browserLanguage: "ru-RU" })).toBe("ru-RU");
  });

  it("uses the browser's language when the host locale differs and the browser does not list it", () => {
    expect(resolveLanguage({ uiLocale: "en", browserLanguages: ["ru-RU"], browserLanguage: "ru-RU" })).toBe("ru-RU");
    expect(resolveLanguage({ uiLocale: "ru", browserLanguages: ["en-US"], browserLanguage: "en-US" })).toBe("en-US");
  });

  it("skips a leading language dictation cannot serve and takes the next", () => {
    expect(resolveLanguage({ browserLanguages: ["xx-XX", "de-DE"], browserLanguage: "xx-XX" })).toBe("de-DE");
  });

  it("falls back to the Intl locale, then to English", () => {
    expect(resolveLanguage({ intlLocale: "ko-KR" })).toBe("ko-KR");
    expect(resolveLanguage({})).toBe("en-US");
  });
});
