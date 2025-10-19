/**
 * Hook for infinite scroll chat sessions
 * Uses SWR Infinite for pagination
 */

import useSWRInfinite from 'swr/infinite';
import { api, Fetchers, CfgKnowbaseTypes } from '@djangocfg/api';
import type { API } from '@djangocfg/api';

type PaginatedChatSessionList = CfgKnowbaseTypes.PaginatedChatSessionList;
type ChatSession = CfgKnowbaseTypes.ChatSession;

const PAGE_SIZE = 20;

export function useInfiniteSessions() {
  const getKey = (pageIndex: number, previousPageData: PaginatedChatSessionList | null) => {
    // Reached the end
    if (previousPageData && !previousPageData.has_next) return null;
    
    // First page, no previous data
    if (pageIndex === 0) return ['cfg-knowbase-admin-sessions-infinite', 1, PAGE_SIZE];
    
    // Add the page number to the SWR key
    return ['cfg-knowbase-admin-sessions-infinite', pageIndex + 1, PAGE_SIZE];
  };

  const fetcher = async ([, page, pageSize]: [string, number, number]) => {
    return Fetchers.getKnowbaseAdminSessionsList(
      { page, page_size: pageSize },
      api as unknown as API
    );
  };

  const {
    data,
    error,
    isLoading,
    isValidating,
    size,
    setSize,
    mutate,
  } = useSWRInfinite<PaginatedChatSessionList>(getKey, fetcher, {
    revalidateFirstPage: false,
    parallel: false,
  });

  // Flatten all pages into single array
  const sessions: ChatSession[] = data ? data.flatMap((page) => page.results) : [];
  
  // Check if there are more pages
  const hasMore = data && data[data.length - 1]?.has_next;
  
  // Total count from last page
  const totalCount = data && data[data.length - 1]?.count;
  
  // Loading more state
  const isLoadingMore = isValidating && data && typeof data[size - 1] !== 'undefined';

  // Function to load next page
  const loadMore = () => {
    if (hasMore && !isLoadingMore) {
      setSize(size + 1);
    }
  };

  // Refresh all pages
  const refresh = async () => {
    await mutate();
  };

  return {
    sessions,
    isLoading,
    isLoadingMore: isLoadingMore || false,
    error,
    hasMore: hasMore || false,
    totalCount: totalCount || 0,
    loadMore,
    refresh,
  };
}

