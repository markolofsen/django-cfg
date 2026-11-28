/**
 * Type probe (H2.7): `{ ...drfPageParams }` and `{ ...drfCursorParams }` spread into an Orval infinite hook.
 *
 * `tsc --noEmit` (the `check` script) skips `__tests__`, so this test runs the compiler itself on a probe that
 * mirrors Orval 8's `use<Op>Infinite` signature: `query` is `Partial<UseInfiniteQueryOptions<…, Params['page']>>`
 * and the page param is the optional query parameter's type. This package's generated tree has no infinite hook
 * (the `infinite` Target option is off here), so the probe carries its own copy of the shape, the one the
 * generator emits for `realtime_demo_pings_list`.
 */

import path from 'node:path';

import ts from 'typescript';
import { describe, expect, it } from 'vitest';

const PACKAGE_ROOT = path.resolve(__dirname, '../../..');
const PROBE = path.join(__dirname, '__pagination_probe__.ts');

const probeSource = `
import { useInfiniteQuery } from '@tanstack/react-query';
import type { InfiniteData, QueryKey, UseInfiniteQueryOptions } from '@tanstack/react-query';

import { drfCursorParams, drfPageParams } from '../pagination';

type PingsListParams = { page?: number; page_size?: number };
type PaginatedPingList = {
  count: number; page: number; pages: number; page_size: number;
  has_next: boolean; has_previous: boolean;
  next_page?: number | null; previous_page?: number | null;
  results: { id: number }[];
};
declare const pingsList: (params?: PingsListParams) => Promise<PaginatedPingList>;

export function usePingsListInfinite<
  TData = InfiniteData<PaginatedPingList, PingsListParams['page']>,
  TError = unknown,
>(
  params?: PingsListParams,
  options?: {
    query?: Partial<UseInfiniteQueryOptions<PaginatedPingList, TError, TData, QueryKey, PingsListParams['page']>>;
  },
) {
  return useInfiniteQuery({
    queryKey: ['infinite', '/realtime/demo/pings/', params],
    queryFn: ({ pageParam }) => pingsList({ ...params, page: pageParam ?? params?.page }),
    ...options?.query,
  } as UseInfiniteQueryOptions<PaginatedPingList, TError, TData, QueryKey, PingsListParams['page']>);
}

type CommentsListParams = { object_id: string; cursor?: string };
type CommentList = { next_cursor?: string | null; results: { id: string }[] };
declare const commentsList: (params: CommentsListParams) => Promise<CommentList>;

export function useCommentsListInfinite<
  TData = InfiniteData<CommentList, CommentsListParams['cursor']>,
  TError = unknown,
>(
  params: CommentsListParams,
  options?: {
    query?: Partial<UseInfiniteQueryOptions<CommentList, TError, TData, QueryKey, CommentsListParams['cursor']>>;
  },
) {
  return useInfiniteQuery({
    queryKey: ['infinite', '/comments/', params],
    queryFn: ({ pageParam }) => commentsList({ ...params, cursor: pageParam ?? params.cursor }),
    ...options?.query,
  } as UseInfiniteQueryOptions<CommentList, TError, TData, QueryKey, CommentsListParams['cursor']>);
}

export const pings = () => usePingsListInfinite({ page_size: 20 }, { query: { ...drfPageParams } });
export const comments = () => useCommentsListInfinite({ object_id: 'x' }, { query: { ...drfCursorParams } });
`;

const diagnosticsOf = (): string[] => {
  const configPath = path.join(PACKAGE_ROOT, 'tsconfig.json');
  const config = ts.readConfigFile(configPath, ts.sys.readFile);
  const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, PACKAGE_ROOT);
  const options: ts.CompilerOptions = { ...parsed.options, noEmit: true, declaration: false, declarationMap: false };

  const host = ts.createCompilerHost(options, true);
  const getSourceFile = host.getSourceFile.bind(host);
  host.getSourceFile = (fileName, languageVersion, ...rest) =>
    path.resolve(fileName) === PROBE
      ? ts.createSourceFile(fileName, probeSource, languageVersion, true)
      : getSourceFile(fileName, languageVersion, ...rest);
  const fileExists = host.fileExists.bind(host);
  host.fileExists = (fileName) => path.resolve(fileName) === PROBE || fileExists(fileName);

  const program = ts.createProgram([PROBE], options, host);
  const probe = program.getSourceFile(PROBE);
  return ts.getPreEmitDiagnostics(program, probe).map((d) => ts.flattenDiagnosticMessageText(d.messageText, '\n'));
};

describe('page params against the generated infinite hook (type probe)', () => {
  it('spreads drfPageParams and drfCursorParams without a type error', () => {
    expect(diagnosticsOf()).toEqual([]);
  }, 60_000);
});
