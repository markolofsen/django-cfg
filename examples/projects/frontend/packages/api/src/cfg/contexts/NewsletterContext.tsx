/**
 * Newsletter Context
 * 
 * Manages newsletter campaigns and subscriptions using generated SWR hooks
 * 
 * Features:
 * - Campaign management (create, update, delete, send)
 * - Subscription management (subscribe, unsubscribe)
 * - Campaign lists with pagination
 * - Subscription lists with pagination
 */

"use client";

import { createContext, useContext, ReactNode } from 'react';
import { SWRConfig, useSWRConfig } from 'swr';
import { api } from '../BaseClient';
import {
  useNewsletterCampaignsList,
  useNewsletterCampaignsRetrieve,
  useCreateNewsletterCampaignsCreate,
  useUpdateNewsletterCampaignsUpdate,
  usePartialUpdateNewsletterCampaignsPartialUpdate,
  useDeleteNewsletterCampaignsDestroy,
  useCreateNewsletterCampaignsSendCreate,
  useNewsletterSubscriptionsList,
  useCreateNewsletterSubscribeCreate,
  useCreateNewsletterUnsubscribeCreate,
} from '../generated/_utils/hooks';
import type { API } from '../generated';
import type {
  NewsletterCampaign,
  NewsletterCampaignRequest,
  PatchedNewsletterCampaignRequest,
  NewsletterSubscription,
  PaginatedNewsletterCampaignList,
  PaginatedNewsletterSubscriptionList,
  SubscribeRequest,
  SubscribeResponse,
  UnsubscribeRequest,
  SuccessResponse,
  SendCampaignRequest,
  SendCampaignResponse,
} from '../generated/_utils/schemas';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface NewsletterContextValue {
  // Campaigns list state
  campaigns: NewsletterCampaign[];
  isLoadingCampaigns: boolean;
  campaignsError: Error | null;
  pagination?: {
    count: number;
    next: number | null;
    previous: number | null;
  };

  // Campaign operations
  getCampaign: (id: number) => { data?: NewsletterCampaign; error?: Error; isLoading: boolean };
  createCampaign: (data: NewsletterCampaignRequest) => Promise<NewsletterCampaign>;
  updateCampaign: (id: number, data: NewsletterCampaignRequest) => Promise<NewsletterCampaign>;
  partialUpdateCampaign: (id: number, data: PatchedNewsletterCampaignRequest) => Promise<NewsletterCampaign>;
  deleteCampaign: (id: number) => Promise<void>;
  sendCampaign: (campaignId: number) => Promise<SendCampaignResponse>;

  // Subscriptions list state
  subscriptions: NewsletterSubscription[];
  isLoadingSubscriptions: boolean;
  subscriptionsError: Error | null;

  // Subscription operations
  subscribe: (data: SubscribeRequest) => Promise<SubscribeResponse>;
  unsubscribe: (data: UnsubscribeRequest) => Promise<SuccessResponse>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const NewsletterContext = createContext<NewsletterContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider Props
// ─────────────────────────────────────────────────────────────────────────

interface NewsletterProviderProps {
  children: ReactNode;
  page?: number;
  pageSize?: number;
}

// ─────────────────────────────────────────────────────────────────────────
// Provider Component
// ─────────────────────────────────────────────────────────────────────────

export function NewsletterProvider({ 
  children, 
  page = 1, 
  pageSize = 100 
}: NewsletterProviderProps) {
  const { mutate } = useSWRConfig();
  
  const swrConfig = {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    revalidateIfStale: false,
  };

  // List params for proper revalidation
  const listParams = { page, page_size: pageSize };

  // Campaigns list
  const {
    data: campaignsData,
    error: campaignsError,
    isLoading: isLoadingCampaigns,
  } = useNewsletterCampaignsList(listParams, api as unknown as API);

  // Subscriptions list
  const {
    data: subscriptionsData,
    error: subscriptionsError,
    isLoading: isLoadingSubscriptions,
  } = useNewsletterSubscriptionsList(listParams, api as unknown as API);

  // Mutation hooks
  const createCampaignMutation = useCreateNewsletterCampaignsCreate();
  const updateCampaignMutation = useUpdateNewsletterCampaignsUpdate();
  const partialUpdateCampaignMutation = usePartialUpdateNewsletterCampaignsPartialUpdate();
  const deleteCampaignMutation = useDeleteNewsletterCampaignsDestroy();
  const sendCampaignMutation = useCreateNewsletterCampaignsSendCreate();
  const subscribeMutation = useCreateNewsletterSubscribeCreate();
  const unsubscribeMutation = useCreateNewsletterUnsubscribeCreate();

  // Extract data from paginated responses
  const campaigns = campaignsData?.results || [];
  const subscriptions = subscriptionsData?.results || [];

  // Get single campaign
  const getCampaign = (id: number) => {
    const { data, error, isLoading } = useNewsletterCampaignsRetrieve(id, api as unknown as API);
    return { data, error, isLoading };
  };

  // Create campaign
  const createCampaign = async (data: NewsletterCampaignRequest): Promise<NewsletterCampaign> => {
    const result = await createCampaignMutation(data, api as unknown as API);
    await mutate(['cfg-newsletter-campaigns-list', listParams]);
    return result as NewsletterCampaign;
  };

  // Update campaign (full)
  const updateCampaign = async (id: number, data: NewsletterCampaignRequest): Promise<NewsletterCampaign> => {
    const result = await updateCampaignMutation(id, data, api as unknown as API);
    await mutate(['cfg-newsletter-campaigns-list', listParams]);
    await mutate(['cfg-newsletter-campaigns-retrieve', id]);
    return result as NewsletterCampaign;
  };

  // Partial update campaign (currently not supported by generated API)
  const partialUpdateCampaign = async (id: number, data: PatchedNewsletterCampaignRequest): Promise<NewsletterCampaign> => {
    // TODO: Fix generator to include data parameter for PATCH requests
    // const result = await partialUpdateCampaignMutation(id, data, api as unknown as API);
    // For now, fallback to full update
    const result = await updateCampaignMutation(id, data as NewsletterCampaignRequest, api as unknown as API);
    await mutate(['cfg-newsletter-campaigns-list', listParams]);
    await mutate(['cfg-newsletter-campaigns-retrieve', id]);
    return result as NewsletterCampaign;
  };

  // Delete campaign
  const deleteCampaign = async (id: number): Promise<void> => {
    await deleteCampaignMutation(id, api as unknown as API);
    await mutate(['cfg-newsletter-campaigns-list', listParams]);
  };

  // Send campaign
  const sendCampaign = async (campaignId: number): Promise<SendCampaignResponse> => {
    const result = await sendCampaignMutation({ campaign_id: campaignId }, api as unknown as API);
    await mutate(['cfg-newsletter-campaigns-list', listParams]);
    await mutate(['cfg-newsletter-campaigns-retrieve', campaignId]);
    return result as SendCampaignResponse;
  };

  // Subscribe
  const subscribe = async (data: SubscribeRequest): Promise<SubscribeResponse> => {
    const result = await subscribeMutation(data, api as unknown as API);
    await mutate(['cfg-newsletter-subscriptions-list', listParams]);
    return result as SubscribeResponse;
  };

  // Unsubscribe
  const unsubscribe = async (data: UnsubscribeRequest): Promise<SuccessResponse> => {
    const result = await unsubscribeMutation(data, api as unknown as API);
    await mutate(['cfg-newsletter-subscriptions-list', listParams]);
    return result as SuccessResponse;
  };

  const value: NewsletterContextValue = {
    campaigns,
    isLoadingCampaigns,
    campaignsError,
    pagination: campaignsData ? {
      count: campaignsData.count,
      next: campaignsData.next_page ?? null,
      previous: campaignsData.previous_page ?? null,
    } : undefined,
    getCampaign,
    createCampaign,
    updateCampaign,
    partialUpdateCampaign,
    deleteCampaign,
    sendCampaign,
    subscriptions,
    isLoadingSubscriptions,
    subscriptionsError,
    subscribe,
    unsubscribe,
  };

  return (
    <SWRConfig value={swrConfig}>
      <NewsletterContext.Provider value={value}>
        {children}
      </NewsletterContext.Provider>
    </SWRConfig>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useNewsletterContext(): NewsletterContextValue {
  const context = useContext(NewsletterContext);
  if (!context) {
    throw new Error('useNewsletterContext must be used within NewsletterProvider');
  }
  return context;
}

