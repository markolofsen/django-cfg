/**
 * Hook for infinite scroll support messages
 * Uses SWR Infinite for pagination
 */

import useSWRInfinite from 'swr/infinite';
import { api, Fetchers, CfgSupportTypes } from '@djangocfg/api';
import type { API } from '@djangocfg/api';

type PaginatedMessageList = CfgSupportTypes.PaginatedMessageList;
type Message = CfgSupportTypes.Message;

const PAGE_SIZE = 20;

interface UseInfiniteMessagesReturn {
  messages: Message[];
  isLoading: boolean;
  isLoadingMore: boolean;
  error: any;
  hasMore: boolean;
  totalCount: number;
  loadMore: () => void;
  refresh: () => Promise<void>;
  addMessage: (message: Message) => void;
}

export function useInfiniteMessages(ticketUuid: string | null): UseInfiniteMessagesReturn {
  const getKey = (pageIndex: number, previousPageData: PaginatedMessageList | null) => {
    // No ticket selected
    if (!ticketUuid) return null;

    // Reached the end
    if (previousPageData && !previousPageData.has_next) return null;

    // First page, no previous data
    if (pageIndex === 0) return ['cfg-support-messages-infinite', ticketUuid, 1, PAGE_SIZE];

    // Add the page number to the SWR key
    return ['cfg-support-messages-infinite', ticketUuid, pageIndex + 1, PAGE_SIZE];
  };

  const fetcher = async ([, ticket_uuid, page, pageSize]: [string, string, number, number]) => {
    return Fetchers.getSupportTicketsMessagesList(
      ticket_uuid,
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
  } = useSWRInfinite<PaginatedMessageList>(getKey, fetcher, {
    revalidateFirstPage: false,
    parallel: false,
  });

  // Flatten all pages into single array (reversed for chat display)
  const messages: Message[] = data ? data.flatMap((page) => page.results) : [];

  // Check if there are more pages
  const hasMore = data && data[data.length - 1]?.has_next;

  // Total count from last page
  const totalCount = data && data[data.length - 1]?.count;

  // Loading more state
  const isLoadingMore = !!(isValidating && data && typeof data[size - 1] !== 'undefined');

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

  // Add new message optimistically
  const addMessage = (message: Message) => {
    if (!data || !data[0]) return;

    // Add the message to the first page
    const newData = [...data];
    const firstPage = newData[0];

    if (firstPage) {
      newData[0] = {
        ...firstPage,
        results: [message, ...firstPage.results],
        count: firstPage.count + 1,
        page: firstPage.page || 1,
        pages: firstPage.pages || 1,
      };
    }

    mutate(newData, false);
  };

  return {
    messages,
    isLoading,
    isLoadingMore: isLoadingMore || false,
    error,
    hasMore: hasMore || false,
    totalCount: totalCount || 0,
    loadMore,
    refresh,
    addMessage,
  };
}