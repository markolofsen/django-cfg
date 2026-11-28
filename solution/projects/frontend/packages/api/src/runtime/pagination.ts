/**
 * Page-param options for TanStack `useInfiniteQuery` over django-cfg list envelopes (plan H2.7, runtime half).
 *
 * Orval generates the infinite hooks (`override.query.useInfinite`) but not `getNextPageParam`, so a consumer
 * spreads one of these into the hook's `query` options:
 *
 *   useCatalogTitlesListInfinite(params, { query: { ...drfPageParams } });
 *
 * The envelopes, read from the specs:
 * - page numbers: django-cfg `DefaultPagination` (`django_cfg/middleware/pagination.py`), every `Paginated*` model:
 *   `page`, `pages`, `has_next`, `has_previous`, `next_page`, `previous_page`, `results`;
 * - cursors: kino's comment lists (`CommentList`, `MyCommentList`, `ReplyList`) carry `next_cursor` and take a
 *   `cursor` query parameter; DRF's own `CursorPagination` carries a `next` URL with `?cursor=`.
 */

export interface PageParamOptions<TPage, TParam> {
  initialPageParam: TParam;
  getNextPageParam: (lastPage: TPage, allPages: TPage[], lastPageParam: TParam) => TParam | undefined;
  getPreviousPageParam: (firstPage: TPage, allPages: TPage[], firstPageParam: TParam) => TParam | undefined;
}

/** The fields of a django-cfg page-number envelope that page params read. */
export interface DrfPageEnvelope {
  page?: number | null;
  has_next?: boolean | null;
  has_previous?: boolean | null;
  next_page?: number | null;
  previous_page?: number | null;
}

/** The fields of a cursor envelope that page params read. */
export interface DrfCursorEnvelope {
  next_cursor?: string | null;
  previous_cursor?: string | null;
  next?: string | null;
  previous?: string | null;
}

const isPage = (value: unknown): value is number => typeof value === 'number' && Number.isInteger(value) && value > 0;

/** `next_page` when the envelope gives it, else the current page plus one while `has_next`. */
const adjacentPage = (
  page: DrfPageEnvelope | undefined,
  param: number | undefined,
  explicit: 'next_page' | 'previous_page',
  flag: 'has_next' | 'has_previous',
  step: 1 | -1,
): number | undefined => {
  if (!page) return undefined;
  const given = page[explicit];
  if (isPage(given)) return given;
  if (page[flag] !== true) return undefined;
  const current = isPage(page.page) ? page.page : (param ?? 1);
  const adjacent = current + step;
  return isPage(adjacent) ? adjacent : undefined;
};

/**
 * Page numbers from 1: `next_page`, else `page + 1` while `has_next`; `undefined` ends the list.
 *
 * The param is `number | undefined` because that is how Orval types it (`Params['page']`, an optional query
 * parameter); typed `number`, the spread fails against the generated hook (TS2769, strictFunctionTypes).
 */
export const drfPageParams: PageParamOptions<DrfPageEnvelope, number | undefined> = {
  initialPageParam: 1,
  getNextPageParam: (lastPage, _allPages, lastPageParam) =>
    adjacentPage(lastPage, lastPageParam, 'next_page', 'has_next', 1),
  getPreviousPageParam: (firstPage, _allPages, firstPageParam) =>
    adjacentPage(firstPage, firstPageParam, 'previous_page', 'has_previous', -1),
};

/** The cursor in an envelope: the `*_cursor` field, else the `cursor` query parameter of the `next`/`previous` URL. */
const cursorOf = (cursor: unknown, link: unknown): string | undefined => {
  if (typeof cursor === 'string' && cursor) return cursor;
  if (typeof link !== 'string' || !link) return undefined;
  try {
    return new URL(link, 'http://relative.invalid').searchParams.get('cursor') || undefined;
  } catch {
    return undefined;
  }
};

/**
 * Cursors: the first page has none (`undefined` leaves `cursor` out of the query), the next one comes from
 * `next_cursor` or the `next` URL; `undefined` ends the list.
 */
export const drfCursorParams: PageParamOptions<DrfCursorEnvelope, string | undefined> = {
  initialPageParam: undefined,
  getNextPageParam: (lastPage) => cursorOf(lastPage?.next_cursor, lastPage?.next),
  getPreviousPageParam: (firstPage) => cursorOf(firstPage?.previous_cursor, firstPage?.previous),
};
