import { describe, expect, it } from "vitest"

import { formatDayOfMonth, formatTimeOfDay, startsNewDay } from "./time"

const at = (iso: string) => Date.parse(iso)

describe("startsNewDay", () => {
  it("opens a feed with a divider", () => {
    expect(startsNewDay(at("2026-08-26T00:23:00"), undefined)).toBe(true)
  })

  it("keeps consecutive rows of one day together", () => {
    expect(startsNewDay(at("2026-08-26T23:59:00"), at("2026-08-26T00:01:00"))).toBe(false)
  })

  it("breaks across midnight", () => {
    expect(startsNewDay(at("2026-08-27T00:01:00"), at("2026-08-26T23:59:00"))).toBe(true)
  })

  it("breaks between the same day of different years", () => {
    // The reason this compares days and not labels: both render identically
    // under a format that omits the year, so a label comparison would merge
    // facts twelve months apart under one heading.
    expect(startsNewDay(at("2026-08-26T12:00:00"), at("2025-08-26T12:00:00"))).toBe(true)
  })
})

describe("formatDayOfMonth", () => {
  it("carries the year, so two Augusts are distinguishable", () => {
    const thisYear = formatDayOfMonth(at("2026-08-26T12:00:00"), "en")
    const lastYear = formatDayOfMonth(at("2025-08-26T12:00:00"), "en")
    expect(thisYear).not.toBe(lastYear)
    expect(thisYear).toContain("2026")
  })

  it("carries no clock", () => {
    expect(formatDayOfMonth(at("2026-08-26T13:45:00"), "en")).not.toMatch(/\d{1,2}[:.]\d{2}/)
  })
})

describe("formatTimeOfDay", () => {
  it("renders the clock without a date", () => {
    const label = formatTimeOfDay(at("2026-08-26T13:45:00"), "en")
    expect(label).toMatch(/\d{1,2}[:.]\d{2}/)
    expect(label).not.toContain("2026")
  })

  it("follows the locale's own clock convention", () => {
    // `en` is 12-hour, `ru` is 24-hour — the reason this is not a hardcoded
    // `HH:mm`, which would impose one convention on every reader.
    //
    // This is also the regression guard for the formatter's implementation.
    // A library that ships locale data as separate bundled modules answers `ru`
    // with the English rendering when only `en` was imported, which reached the
    // running console as "2:47 AM" under `<html lang="ru">`. `Intl` reads the
    // platform's data, so both spellings are available with nothing bundled.
    expect(formatTimeOfDay(at("2026-08-26T13:45:00"), "en")).toMatch(/PM/i)
    expect(formatTimeOfDay(at("2026-08-26T13:45:00"), "ru")).toContain("13")
    expect(formatTimeOfDay(at("2026-08-26T13:45:00"), "ru")).not.toMatch(/[AP]M/i)
  })

  it("returns an empty string for an unparseable input", () => {
    expect(formatTimeOfDay("not a date")).toBe("")
  })
})
