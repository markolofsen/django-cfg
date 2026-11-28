/**
 * Query string parsers — typed marshalling between URL strings and JS values.
 *
 * WHY:
 *   `URLSearchParams.get('page')` is always a string. Coercing it
 *   inside every component (`Number(...) || 1`) is repetitive and
 *   error-prone. A parser bakes in `parse(string) → T | null` and
 *   `serialize(T) → string`, plus optional equality (so we can clear
 *   default values from the URL — known as `clearOnDefault`).
 *
 *   Parsers are zero-runtime objects — pure functions in plain
 *   structures. No deps, no validation libraries. If a consumer wants
 *   zod / standard-schema, they wrap `parseAsJson` themselves.
 *
 * @example
 *   import { useQueryState, parseAsInteger, parseAsString } from '@djangocfg/ui-core/hooks';
 *   const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1));
 *   const [q,    setQ]    = useQueryState('q',    parseAsString);
 */

/** Convert a URL string value into a typed value, or `null` on parse failure. */
export interface QueryParser<T> {
  parse: (value: string) => T | null;
  serialize: (value: T) => string;
  /** Equality check, used by `clearOnDefault` to strip default values from the URL. */
  eq: (a: T, b: T) => boolean;
  /** Optional default. When set, missing key returns it instead of `null`. */
  defaultValue?: T;
}

/** Builder — adds `withDefault` chain on top of a parser. */
export interface QueryParserBuilder<T> extends QueryParser<T> {
  withDefault(value: T): QueryParser<T> & { defaultValue: T };
}

function builder<T>(parser: Omit<QueryParser<T>, 'eq'> & { eq?: QueryParser<T>['eq'] }): QueryParserBuilder<T> {
  const eq = parser.eq ?? ((a, b) => a === b);
  const base: QueryParser<T> = { ...parser, eq };
  return {
    ...base,
    withDefault(defaultValue: T) {
      return { ...base, defaultValue };
    },
  };
}

// ────────────────────────────────────────────────────────────────────
// Built-in parsers
// ────────────────────────────────────────────────────────────────────

export const parseAsString: QueryParserBuilder<string> = builder({
  parse: (v) => v,
  serialize: (v) => v,
});

export const parseAsInteger: QueryParserBuilder<number> = builder({
  parse: (v) => {
    const n = Number.parseInt(v, 10);
    return Number.isFinite(n) ? n : null;
  },
  serialize: (v) => String(v),
});

export const parseAsFloat: QueryParserBuilder<number> = builder({
  parse: (v) => {
    const n = Number.parseFloat(v);
    return Number.isFinite(n) ? n : null;
  },
  serialize: (v) => String(v),
});

export const parseAsBoolean: QueryParserBuilder<boolean> = builder({
  // `?debug` (no value) → true, `?debug=true` → true, `?debug=false` → false.
  parse: (v) => v === '' || v === 'true' || v === '1',
  serialize: (v) => (v ? 'true' : 'false'),
});

export const parseAsIsoDate: QueryParserBuilder<Date> = builder({
  parse: (v) => {
    const ms = Date.parse(v);
    return Number.isFinite(ms) ? new Date(ms) : null;
  },
  serialize: (v) => v.toISOString(),
  eq: (a, b) => a.getTime() === b.getTime(),
});

/**
 * `parseAsStringEnum(['asc','desc'])` — restricts values to a fixed list.
 * Returns `null` on anything outside the set, so `withDefault` falls back.
 */
export function parseAsStringEnum<T extends string>(
  values: readonly T[]
): QueryParserBuilder<T> {
  const set = new Set<string>(values);
  return builder({
    parse: (v) => (set.has(v) ? (v as T) : null),
    serialize: (v) => v,
  });
}

/**
 * `parseAsArrayOf(parseAsInteger)` — comma-separated list of typed values.
 * Empty array serializes to empty string (which `useQueryState` strips).
 */
export function parseAsArrayOf<T>(
  itemParser: QueryParser<T>,
  separator: string = ','
): QueryParserBuilder<T[]> {
  return builder({
    parse: (v) => {
      if (v === '') return [];
      const parts = v.split(separator);
      const out: T[] = [];
      for (const part of parts) {
        const parsed = itemParser.parse(part);
        if (parsed === null) return null;
        out.push(parsed);
      }
      return out;
    },
    serialize: (arr) => arr.map(itemParser.serialize).join(separator),
    eq: (a, b) => {
      if (a.length !== b.length) return false;
      for (let i = 0; i < a.length; i++) {
        if (!itemParser.eq(a[i] as T, b[i] as T)) return false;
      }
      return true;
    },
  });
}

/**
 * `parseAsJson<{ a: number }>()` — JSON-encode complex shapes.
 * Pass a guard for runtime validation; without one any JSON-parsable
 * value passes (TypeScript-only safety).
 */
export function parseAsJson<T>(
  guard?: (value: unknown) => value is T
): QueryParserBuilder<T> {
  return builder({
    parse: (v) => {
      try {
        const parsed = JSON.parse(v) as unknown;
        if (guard && !guard(parsed)) return null;
        return parsed as T;
      } catch {
        return null;
      }
    },
    serialize: (value) => JSON.stringify(value),
    // Identity by JSON shape — fine for small objects, expensive for big ones.
    eq: (a, b) => JSON.stringify(a) === JSON.stringify(b),
  });
}
