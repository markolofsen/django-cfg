/**
 * Knowbase Documents Context
 * Context for managing documents and archives
 */

'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '../../BaseClient';
import {
  useKnowbaseAdminDocumentsList,
  useKnowbaseAdminDocumentsRetrieve,
  useCreateKnowbaseAdminDocumentsCreate,
  useUpdateKnowbaseAdminDocumentsUpdate,
  usePartialUpdateKnowbaseAdminDocumentsPartialUpdate,
  useDeleteKnowbaseAdminDocumentsDestroy,
  useCreateKnowbaseAdminDocumentsReprocessCreate,
  useKnowbaseAdminDocumentsStatusRetrieve,
  useKnowbaseAdminDocumentsStatsRetrieve,
  useKnowbaseSystemArchivesList,
  useKnowbaseSystemArchivesRetrieve,
  useCreateKnowbaseSystemArchivesCreate,
  useUpdateKnowbaseSystemArchivesUpdate,
  usePartialUpdateKnowbaseSystemArchivesPartialUpdate,
  useDeleteKnowbaseSystemArchivesDestroy,
  useKnowbaseSystemArchivesStatisticsRetrieve,
} from '../../generated/_utils/hooks/cfg__knowbase';
import type { API } from '../../generated';
import type {
  PaginatedDocumentList,
  Document,
  DocumentCreateRequest,
  DocumentRequest,
  PatchedDocumentRequest,
  DocumentProcessingStatus,
  DocumentStats,
  PaginatedDocumentArchiveListList,
  DocumentArchive,
  DocumentArchiveDetail,
  PatchedDocumentArchiveRequest,
  ArchiveProcessingResult,
  ArchiveStatistics,
} from '../../generated/cfg__knowbase/models';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface KnowbaseDocumentsContextValue {
  // Documents list
  documents: PaginatedDocumentList | undefined;
  isLoadingDocuments: boolean;
  documentsError: Error | undefined;
  refreshDocuments: () => Promise<void>;

  // Document operations
  getDocument: (id: string) => Promise<Document | undefined>;
  getDocumentStatus: (id: string) => Promise<DocumentProcessingStatus | undefined>;
  getDocumentStats: () => Promise<DocumentStats | undefined>;
  createDocument: (data: DocumentCreateRequest) => Promise<Document>;
  updateDocument: (id: string, data: DocumentRequest) => Promise<Document>;
  partialUpdateDocument: (id: string, data: PatchedDocumentRequest) => Promise<Document>;
  deleteDocument: (id: string) => Promise<void>;
  reprocessDocument: (id: string, data: DocumentRequest) => Promise<Document>;

  // Archives list
  archives: PaginatedDocumentArchiveListList | undefined;
  isLoadingArchives: boolean;
  archivesError: Error | undefined;
  refreshArchives: () => Promise<void>;

  // Archive operations
  getArchive: (id: string) => Promise<DocumentArchiveDetail | undefined>;
  getArchiveStatistics: () => Promise<ArchiveStatistics | undefined>;
  createArchive: (data: FormData) => Promise<ArchiveProcessingResult>;
  updateArchive: (
    id: string,
    title: string,
    archive_file: File | Blob,
    description?: string,
    is_public?: boolean
  ) => Promise<DocumentArchive>;
  partialUpdateArchive: (id: string, data: PatchedDocumentArchiveRequest) => Promise<DocumentArchive>;
  deleteArchive: (id: string) => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const KnowbaseDocumentsContext = createContext<KnowbaseDocumentsContextValue | undefined>(
  undefined
);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function KnowbaseDocumentsProvider({ children }: { children: ReactNode }) {
  // Documents list
  const {
    data: documents,
    error: documentsError,
    isLoading: isLoadingDocuments,
    mutate: mutateDocuments,
  } = useKnowbaseAdminDocumentsList({}, api as unknown as API);

  const refreshDocuments = async () => {
    await mutateDocuments();
  };

  // Archives list
  const {
    data: archives,
    error: archivesError,
    isLoading: isLoadingArchives,
    mutate: mutateArchives,
  } = useKnowbaseSystemArchivesList({}, api as unknown as API);

  const refreshArchives = async () => {
    await mutateArchives();
  };

  // Document mutations
  const createDocumentMutation = useCreateKnowbaseAdminDocumentsCreate();
  const updateDocumentMutation = useUpdateKnowbaseAdminDocumentsUpdate();
  const partialUpdateDocumentMutation = usePartialUpdateKnowbaseAdminDocumentsPartialUpdate();
  const deleteDocumentMutation = useDeleteKnowbaseAdminDocumentsDestroy();
  const reprocessDocumentMutation = useCreateKnowbaseAdminDocumentsReprocessCreate();

  // Archive mutations
  const createArchiveMutation = useCreateKnowbaseSystemArchivesCreate();
  const updateArchiveMutation = useUpdateKnowbaseSystemArchivesUpdate();
  const partialUpdateArchiveMutation = usePartialUpdateKnowbaseSystemArchivesPartialUpdate();
  const deleteArchiveMutation = useDeleteKnowbaseSystemArchivesDestroy();

  // Get single document
  const getDocument = async (id: string): Promise<Document | undefined> => {
    const { data } = useKnowbaseAdminDocumentsRetrieve(id, api as unknown as API);
    return data;
  };

  // Get document status
  const getDocumentStatus = async (id: string): Promise<DocumentProcessingStatus | undefined> => {
    const { data } = useKnowbaseAdminDocumentsStatusRetrieve(id, api as unknown as API);
    return data;
  };

  // Get document stats
  const getDocumentStats = async (): Promise<DocumentStats | undefined> => {
    const { data } = useKnowbaseAdminDocumentsStatsRetrieve(api as unknown as API);
    return data;
  };

  // Create document
  const createDocument = async (data: DocumentCreateRequest): Promise<Document> => {
    const result = await createDocumentMutation(data, api as unknown as API);
    await refreshDocuments();
    return result as Document;
  };

  // Update document
  const updateDocument = async (id: string, data: DocumentRequest): Promise<Document> => {
    const result = await updateDocumentMutation(id, data, api as unknown as API);
    await refreshDocuments();
    return result as Document;
  };

  // Partial update document
  const partialUpdateDocument = async (
    id: string,
    data: PatchedDocumentRequest
  ): Promise<Document> => {
    const result = await partialUpdateDocumentMutation(id, data, api as unknown as API);
    await refreshDocuments();
    return result as Document;
  };

  // Delete document
  const deleteDocument = async (id: string): Promise<void> => {
    await deleteDocumentMutation(id, api as unknown as API);
    await refreshDocuments();
  };

  // Reprocess document
  const reprocessDocument = async (id: string, data: DocumentRequest): Promise<Document> => {
    const result = await reprocessDocumentMutation(id, data, api as unknown as API);
    await refreshDocuments();
    return result as Document;
  };

  // Get single archive
  const getArchive = async (id: string): Promise<DocumentArchiveDetail | undefined> => {
    const { data } = useKnowbaseSystemArchivesRetrieve(id, api as unknown as API);
    return data as DocumentArchiveDetail | undefined;
  };

  // Get archive statistics
  const getArchiveStatistics = async (): Promise<ArchiveStatistics | undefined> => {
    const { data } = useKnowbaseSystemArchivesStatisticsRetrieve(api as unknown as API);
    return data;
  };

  // Create archive
  const createArchive = async (data: FormData): Promise<ArchiveProcessingResult> => {
    const result = await createArchiveMutation(data, api as unknown as API);
    await refreshArchives();
    return result as ArchiveProcessingResult;
  };

  // Update archive
  const updateArchive = async (
    id: string,
    title: string,
    archive_file: File | Blob,
    description?: string,
    is_public?: boolean
  ): Promise<DocumentArchive> => {
    // Note: The hook expects DocumentArchiveRequest, but the client method has different signature
    // This is a type mismatch in the generated code
    const data = { title, archive_file, description, is_public } as any;
    const result = await updateArchiveMutation(id, data, api as unknown as API);
    await refreshArchives();
    return result as DocumentArchive;
  };

  // Partial update archive
  const partialUpdateArchive = async (
    id: string,
    data: PatchedDocumentArchiveRequest
  ): Promise<DocumentArchive> => {
    const result = await partialUpdateArchiveMutation(id, data, api as unknown as API);
    await refreshArchives();
    return result as DocumentArchive;
  };

  // Delete archive
  const deleteArchive = async (id: string): Promise<void> => {
    await deleteArchiveMutation(id, api as unknown as API);
    await refreshArchives();
  };

  const value: KnowbaseDocumentsContextValue = {
    documents,
    isLoadingDocuments,
    documentsError,
    refreshDocuments,
    getDocument,
    getDocumentStatus,
    getDocumentStats,
    createDocument,
    updateDocument,
    partialUpdateDocument,
    deleteDocument,
    reprocessDocument,
    archives: archives as PaginatedDocumentArchiveListList | undefined,
    isLoadingArchives,
    archivesError,
    refreshArchives,
    getArchive,
    getArchiveStatistics,
    createArchive,
    updateArchive,
    partialUpdateArchive,
    deleteArchive,
  };

  return (
    <KnowbaseDocumentsContext.Provider value={value}>
      {children}
    </KnowbaseDocumentsContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useKnowbaseDocumentsContext(): KnowbaseDocumentsContextValue {
  const context = useContext(KnowbaseDocumentsContext);
  if (!context) {
    throw new Error('useKnowbaseDocumentsContext must be used within KnowbaseDocumentsProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types for external use
// ─────────────────────────────────────────────────────────────────────────

export type {
  Document,
  DocumentCreateRequest,
  DocumentRequest,
  PatchedDocumentRequest,
  DocumentProcessingStatus,
  DocumentStats,
  DocumentArchive,
  DocumentArchiveDetail,
  PatchedDocumentArchiveRequest,
  ArchiveProcessingResult,
  ArchiveStatistics,
} from '../../generated/cfg__knowbase/models';

