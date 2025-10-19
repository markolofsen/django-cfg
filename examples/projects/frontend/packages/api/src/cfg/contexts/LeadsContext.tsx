'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { SWRConfig } from 'swr';
import { api } from '../BaseClient';
import {
  useLeadsList,
  useLeadsRetrieve,
  useCreateLeadsCreate,
  useUpdateLeadsUpdate,
  usePartialUpdateLeadsPartialUpdate,
  useDeleteLeadsDestroy,
} from '../generated/_utils/hooks';
import type { API } from '../generated';
import type {
  LeadSubmission,
  LeadSubmissionRequest,
  PatchedLeadSubmissionRequest,
  PaginatedLeadSubmissionList,
} from '../generated/_utils/schemas';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface LeadsContextValue {
  // List operations
  leads: PaginatedLeadSubmissionList | undefined;
  isLoadingLeads: boolean;
  leadsError: Error | undefined;
  refreshLeads: () => Promise<void>;

  // CRUD operations
  getLead: (id: number) => Promise<LeadSubmission | undefined>;
  createLead: (data: LeadSubmissionRequest) => Promise<LeadSubmission>;
  updateLead: (id: number, data: LeadSubmissionRequest) => Promise<LeadSubmission>;
  partialUpdateLead: (id: number, data: PatchedLeadSubmissionRequest) => Promise<LeadSubmission>;
  deleteLead: (id: number) => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const LeadsContext = createContext<LeadsContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function LeadsProvider({ children }: { children: ReactNode }) {
  const swrConfig = {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    revalidateIfStale: false,
  };
  
  // List leads
  const {
    data: leads,
    error: leadsError,
    isLoading: isLoadingLeads,
    mutate: mutateLeads,
  } = useLeadsList({}, api as unknown as API);

  const refreshLeads = async () => {
    await mutateLeads();
  };

  // Mutations
  const createMutation = useCreateLeadsCreate();
  const updateMutation = useUpdateLeadsUpdate();
  const partialUpdateMutation = usePartialUpdateLeadsPartialUpdate();
  const deleteMutation = useDeleteLeadsDestroy();

  // Get single lead
  const getLead = async (id: number): Promise<LeadSubmission | undefined> => {
    const { data } = useLeadsRetrieve(id, api as unknown as API);
    return data;
  };

  // Create lead
  const createLead = async (data: LeadSubmissionRequest): Promise<LeadSubmission> => {
    const result = await createMutation(data, api as unknown as API);
    await refreshLeads();
    return result as LeadSubmission;
  };

  // Update lead
  const updateLead = async (id: number, data: LeadSubmissionRequest): Promise<LeadSubmission> => {
    const result = await updateMutation(id, data, api as unknown as API);
    await refreshLeads();
    return result as LeadSubmission;
  };

  // Partial update lead (currently not supported by generated API)
  const partialUpdateLead = async (
    id: number,
    data: PatchedLeadSubmissionRequest
  ): Promise<LeadSubmission> => {
    // TODO: Fix generator to include data parameter for PATCH requests
    // const result = await partialUpdateMutation(id, data, api as unknown as API);
    // For now, fallback to full update
    const result = await updateMutation(id, data as unknown as LeadSubmissionRequest, api as unknown as API);
    await refreshLeads();
    return result as LeadSubmission;
  };

  // Delete lead
  const deleteLead = async (id: number): Promise<void> => {
    await deleteMutation(id, api as unknown as API);
    await refreshLeads();
  };

  const value: LeadsContextValue = {
    leads,
    isLoadingLeads,
    leadsError,
    refreshLeads,
    getLead,
    createLead,
    updateLead,
    partialUpdateLead,
    deleteLead,
  };

  return (
    <SWRConfig value={swrConfig}>
      <LeadsContext.Provider value={value}>{children}</LeadsContext.Provider>
    </SWRConfig>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useLeadsContext(): LeadsContextValue {
  const context = useContext(LeadsContext);
  if (!context) {
    throw new Error('useLeadsContext must be used within LeadsProvider');
  }
  return context;
}

