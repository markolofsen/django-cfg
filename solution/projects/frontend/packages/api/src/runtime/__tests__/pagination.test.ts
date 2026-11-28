/**
 * H2.7 runtime half: page params for TanStack infinite queries over django-cfg envelopes.
 * The page-number envelope is django-cfg `DefaultPagination`; the cursor one is kino's `CommentList` / DRF
 * `CursorPagination`.
 */
import { describe, expect, it } from 'vitest';

import { drfCursorParams, drfPageParams } from '../pagination';
import * as root from '../../index';

const envelope = (page: number, pages: number) => ({
  count: pages * 10,
  page,
  pages,
  page_size: 10,
  has_next: page < pages,
  has_previous: page > 1,
  next_page: page < pages ? page + 1 : null,
  previous_page: page > 1 ? page - 1 : null,
  results: [],
});

describe('drfPageParams', () => {
  it('starts at page 1 and follows next_page to the end', () => {
    expect(drfPageParams.initialPageParam).toBe(1);
    expect(drfPageParams.getNextPageParam(envelope(1, 3), [], 1)).toBe(2);
    expect(drfPageParams.getNextPageParam(envelope(2, 3), [], 2)).toBe(3);
    expect(drfPageParams.getNextPageParam(envelope(3, 3), [], 3)).toBeUndefined();
  });

  it('falls back to page + 1 while has_next when next_page is absent', () => {
    expect(drfPageParams.getNextPageParam({ page: 4, has_next: true }, [], 4)).toBe(5);
    expect(drfPageParams.getNextPageParam({ has_next: true }, [], 7)).toBe(8);
    expect(drfPageParams.getNextPageParam({ page: 4, has_next: false }, [], 4)).toBeUndefined();
    expect(drfPageParams.getNextPageParam({}, [], 1)).toBeUndefined();
  });

  it('goes back with previous_page or has_previous, never below page 1', () => {
    expect(drfPageParams.getPreviousPageParam(envelope(3, 3), [], 3)).toBe(2);
    expect(drfPageParams.getPreviousPageParam(envelope(1, 3), [], 1)).toBeUndefined();
    expect(drfPageParams.getPreviousPageParam({ page: 1, has_previous: true }, [], 1)).toBeUndefined();
  });
});

describe('drfCursorParams', () => {
  it('starts without a cursor and follows next_cursor', () => {
    expect(drfCursorParams.initialPageParam).toBeUndefined();
    expect(drfCursorParams.getNextPageParam({ next_cursor: 'c2' }, [], undefined)).toBe('c2');
    expect(drfCursorParams.getNextPageParam({ next_cursor: null }, [], 'c2')).toBeUndefined();
    expect(drfCursorParams.getNextPageParam({ next_cursor: '' }, [], 'c2')).toBeUndefined();
  });

  it('reads the cursor from a DRF next URL, absolute or relative', () => {
    expect(drfCursorParams.getNextPageParam({ next: 'https://api.example.test/apix/x/?cursor=cD0yMDIz&page_size=20' }, [], undefined))
      .toBe('cD0yMDIz');
    expect(drfCursorParams.getNextPageParam({ next: '/apix/x/?cursor=abc' }, [], undefined)).toBe('abc');
    expect(drfCursorParams.getNextPageParam({ next: 'https://api.example.test/apix/x/?page=2' }, [], undefined)).toBeUndefined();
    expect(drfCursorParams.getPreviousPageParam({ previous: '/apix/x/?cursor=back' }, [], 'abc')).toBe('back');
  });
});

describe('exports', () => {
  it('are on the package root', () => {
    expect(root.drfPageParams).toBe(drfPageParams);
    expect(root.drfCursorParams).toBe(drfCursorParams);
  });
});
