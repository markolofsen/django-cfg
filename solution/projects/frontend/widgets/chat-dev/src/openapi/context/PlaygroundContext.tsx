'use client';

import consola from 'consola';
import React, {
    createContext, ReactNode, useCallback, useContext, useEffect, useReducer, useRef
} from 'react';

import { useSessionStorage } from '@djangocfg/ui-core/hooks';

import type {
    ApiEndpoint, ApiResponse, PlaygroundConfig, PlaygroundContextType, PlaygroundState,
    PlaygroundStep
} from '../types';
import { parseRequestHeaders } from '../utils';
import { UrlBuilder } from '../utils/url';
import { getDefaultVersion } from '../utils/versionManager';
import { CFG_KEYS } from '@djangocfg/api/storage';

// Session-scoped auth persistence. sessionStorage (not localStorage) so
// the token dies when the browser tab closes — safer default for secrets.
const AUTH_KEY_STORAGE = CFG_KEYS.agentPlaygroundApiKeyId.key;
const AUTH_BEARER_STORAGE = CFG_KEYS.agentPlaygroundBearer.key;

// ─── Initial state ────────────────────────────────────────────────────────────

const createInitialState = (): PlaygroundState => ({
  currentStep: 'endpoints',
  steps: ['endpoints', 'request', 'response'],
  selectedEndpoint: null,
  selectedCategory: 'All',
  searchTerm: '',
  selectedVersion: getDefaultVersion().id,
  requestUrl: '',
  requestMethod: 'GET',
  requestHeaders: '{\n  "Content-Type": "application/json"\n}',
  requestBody: '',
  selectedApiKey: null,
  manualApiToken: '',
  parameters: {},
  response: null,
  loading: false,
  sidebarOpen: false,
  activeSchemaId: null,
});

// ─── Actions ──────────────────────────────────────────────────────────────────

type Action =
  | { type: 'SET_STEP'; step: PlaygroundStep }
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' }
  | { type: 'SELECT_ENDPOINT'; endpoint: ApiEndpoint | null }
  | { type: 'SET_CATEGORY'; category: string }
  | { type: 'SET_SEARCH'; term: string }
  | { type: 'SET_VERSION'; version: string }
  | { type: 'SET_REQUEST_URL'; url: string }
  | { type: 'SET_REQUEST_METHOD'; method: string }
  | { type: 'SET_REQUEST_HEADERS'; headers: string }
  | { type: 'SET_REQUEST_BODY'; body: string }
  | { type: 'SET_API_KEY'; apiKeyId: string | null }
  | { type: 'SET_MANUAL_TOKEN'; token: string }
  | { type: 'SET_PARAMETERS'; parameters: Record<string, string> }
  | { type: 'SET_RESPONSE'; response: ApiResponse | null }
  | { type: 'SET_LOADING'; loading: boolean }
  // Batched: set loading + clear response atomically (avoids two renders on send)
  | { type: 'REQUEST_START' }
  // Batched: set response + loading=false + advance step atomically (avoids three renders)
  | { type: 'REQUEST_SUCCESS'; response: ApiResponse }
  // Batched: set error response + loading=false atomically
  | { type: 'REQUEST_ERROR'; response: ApiResponse }
  | { type: 'SET_SIDEBAR'; open: boolean }
  | { type: 'SET_ACTIVE_SCHEMA_ID'; id: string | null }
  | { type: 'SYNC_API_KEY_HEADER'; headers: string }
  | { type: 'CLEAR_API_KEY_SELECTION' }
  | { type: 'SYNC_URL'; url: string }
  | { type: 'RESET' };

// ─── Reducer ──────────────────────────────────────────────────────────────────

function reducer(state: PlaygroundState, action: Action): PlaygroundState {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, currentStep: action.step };

    case 'NEXT_STEP': {
      const i = state.steps.indexOf(state.currentStep);
      return i < state.steps.length - 1
        ? { ...state, currentStep: state.steps[i + 1]! }
        : state;
    }

    case 'PREV_STEP': {
      const i = state.steps.indexOf(state.currentStep);
      return i > 0 ? { ...state, currentStep: state.steps[i - 1]! } : state;
    }

    case 'SELECT_ENDPOINT': {
      if (!action.endpoint) return { ...state, selectedEndpoint: null };
      // Guard: selecting the same endpoint is a no-op for response state.
      // Without this, clicking "Try it" on the already-loaded endpoint
      // would wipe its response for no reason.
      const same =
        state.selectedEndpoint?.method === action.endpoint.method &&
        state.selectedEndpoint?.path === action.endpoint.path;
      // Pre-fill request body from the OpenAPI example when available.
      // For a brand-new endpoint selection, a realistic example is more
      // useful than the {"key":"value"} placeholder. If the user already
      // has a saved draft, EndpointDraftSync will overwrite this with the
      // persisted value once it hydrates.
      const exampleBody = action.endpoint.requestBody?.example ?? '';
      return {
        ...state,
        selectedEndpoint: action.endpoint,
        requestMethod: action.endpoint.method,
        requestUrl: action.endpoint.path,
        parameters: same ? state.parameters : {},
        requestBody: same ? state.requestBody : exampleBody,
        // Switching to a different endpoint: the previous response no
        // longer belongs here. Clear it so the playground panel collapses
        // back to single-column until the user sends a new request.
        response: same ? state.response : null,
        currentStep: 'request',
      };
    }

    case 'SET_CATEGORY':    return { ...state, selectedCategory: action.category };
    case 'SET_SEARCH':      return { ...state, searchTerm: action.term };
    case 'SET_VERSION':     return { ...state, selectedVersion: action.version };
    case 'SET_REQUEST_URL': return { ...state, requestUrl: action.url };
    case 'SET_REQUEST_METHOD': return { ...state, requestMethod: action.method };
    case 'SET_REQUEST_HEADERS': return { ...state, requestHeaders: action.headers };
    case 'SET_REQUEST_BODY':    return { ...state, requestBody: action.body };
    case 'SET_API_KEY':         return { ...state, selectedApiKey: action.apiKeyId };
    case 'SET_MANUAL_TOKEN':    return { ...state, manualApiToken: action.token };
    case 'SET_PARAMETERS':      return { ...state, parameters: action.parameters };
    case 'SET_RESPONSE':        return { ...state, response: action.response };
    case 'SET_LOADING':         return { ...state, loading: action.loading };

    case 'REQUEST_START':
      return { ...state, loading: true, response: null };

    case 'REQUEST_SUCCESS':
      return { ...state, loading: false, response: action.response, currentStep: 'response' };

    case 'REQUEST_ERROR':
      return { ...state, loading: false, response: action.response };

    case 'SET_SIDEBAR':          return { ...state, sidebarOpen: action.open };
    case 'SET_ACTIVE_SCHEMA_ID': return { ...state, activeSchemaId: action.id };
    case 'SYNC_API_KEY_HEADER':  return { ...state, requestHeaders: action.headers };
    case 'CLEAR_API_KEY_SELECTION': return { ...state, selectedApiKey: null };
    case 'SYNC_URL':             return { ...state, requestUrl: action.url };
    case 'RESET':                return createInitialState();

    default: return state;
  }
}

// ─── Context ──────────────────────────────────────────────────────────────────

const PlaygroundContext = createContext<PlaygroundContextType | undefined>(undefined);

export const usePlaygroundContext = () => {
  const context = useContext(PlaygroundContext);
  if (!context) throw new Error('usePlaygroundContext must be used within a PlaygroundProvider');
  return context;
};

// ─── Provider ─────────────────────────────────────────────────────────────────

interface PlaygroundProviderProps {
  children: ReactNode;
  config: PlaygroundConfig;
}

export const PlaygroundProvider: React.FC<PlaygroundProviderProps> = ({ children, config }) => {
  const [state, dispatch] = useReducer(reducer, undefined, createInitialState);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Closing the panel mid-request must cancel it. Without this the fetch runs
  // on and dispatches a completion for a request the user already abandoned.
  React.useEffect(
    () => () => {
      abortControllerRef.current?.abort();
    },
    [],
  );

  // API keys come from the caller via ``config.apiKeys``. Empty
  // fallback keeps the playground working when the caller hasn't
  // wired any keys yet (public docs / unauthenticated demo).
  const apiKeys = React.useMemo(
    () => config.apiKeys ?? [],
    [config.apiKeys],
  );
  const isLoadingApiKeys = config.apiKeysLoading ?? false;

  // ── Auth persistence (session-scoped) ─────────────────────────────────────
  // Use sessionStorage so the chosen API key / bearer token survive reload
  // within the same tab but die when the tab closes. That matches how
  // users expect auth sessions to work and keeps secrets out of localStorage.
  const [storedApiKeyId, setStoredApiKeyId] = useSessionStorage<string | null>(
    AUTH_KEY_STORAGE,
    null,
  );
  const [storedBearer, setStoredBearer] = useSessionStorage<string>(
    AUTH_BEARER_STORAGE,
    '',
  );
  const hasHydratedAuthRef = useRef(false);

  // Hydrate auth state from sessionStorage exactly once.
  useEffect(() => {
    if (hasHydratedAuthRef.current) return;
    hasHydratedAuthRef.current = true;
    if (storedApiKeyId) dispatch({ type: 'SET_API_KEY', apiKeyId: storedApiKeyId });
    if (storedBearer) dispatch({ type: 'SET_MANUAL_TOKEN', token: storedBearer });
    // We intentionally don't depend on the stored values — this effect
    // runs once on mount; later changes are written out by the effects
    // below, not re-hydrated.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Persist selection → sessionStorage as it changes.
  useEffect(() => {
    if (!hasHydratedAuthRef.current) return;
    setStoredApiKeyId(state.selectedApiKey);
  }, [state.selectedApiKey, setStoredApiKeyId]);

  useEffect(() => {
    if (!hasHydratedAuthRef.current) return;
    setStoredBearer(state.manualApiToken);
  }, [state.manualApiToken, setStoredBearer]);

  // Auto-select first API key — only when there's no persisted selection
  // to restore. Otherwise the first-render auto-pick would clobber a
  // session that had a non-first key chosen.
  useEffect(() => {
    if (!hasHydratedAuthRef.current) return;
    if (!isLoadingApiKeys && apiKeys.length > 0 && !state.selectedApiKey && !storedApiKeyId) {
      dispatch({ type: 'SET_API_KEY', apiKeyId: apiKeys[0]?.id || null });
    }
  }, [apiKeys, isLoadingApiKeys, state.selectedApiKey, storedApiKeyId]);

  // Sync X-API-Key header when selected key changes
  useEffect(() => {
    try {
      const headers = parseRequestHeaders(state.requestHeaders);

      if (state.selectedApiKey) {
        const apiKey = apiKeys.find((k) => k.id === state.selectedApiKey);
        if (!apiKey) {
          dispatch({ type: 'CLEAR_API_KEY_SELECTION' });
          return;
        }
        // Header carries the raw ``secret`` (not the row id) — that's
        // what the server validates. Falls back to ``id`` for legacy
        // callers still on the old ApiKey shape.
        const keyValue = apiKey.secret || apiKey.id;
        if (headers['X-API-Key'] !== keyValue) {
          headers['X-API-Key'] = keyValue;
          dispatch({ type: 'SYNC_API_KEY_HEADER', headers: JSON.stringify(headers, null, 2) });
        }
      } else if (headers['X-API-Key']) {
        delete headers['X-API-Key'];
        dispatch({ type: 'SYNC_API_KEY_HEADER', headers: JSON.stringify(headers, null, 2) });
      }
    } catch (error) {
      consola.error('Error updating headers:', error);
    }
  }, [state.selectedApiKey, apiKeys]); // eslint-disable-line react-hooks/exhaustive-deps

  // Sync URL when path parameters or query parameters change. UrlBuilder
  // handles BOTH path substitution and query string assembly — the old
  // implementation only did the former, which silently dropped every
  // non-path parameter the user entered.
  useEffect(() => {
    if (!state.selectedEndpoint) return;
    const updated = new UrlBuilder(state.selectedEndpoint, state.parameters).build();
    if (updated !== state.requestUrl) {
      dispatch({ type: 'SYNC_URL', url: updated });
    }
  }, [state.parameters, state.selectedEndpoint]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Stable action dispatchers ─────────────────────────────────────────────

  const setCurrentStep    = useCallback((step: PlaygroundStep) => dispatch({ type: 'SET_STEP', step }), []);
  const goToNextStep      = useCallback(() => dispatch({ type: 'NEXT_STEP' }), []);
  const goToPreviousStep  = useCallback(() => dispatch({ type: 'PREV_STEP' }), []);

  const setSelectedEndpoint = useCallback((endpoint: ApiEndpoint | null) =>
    dispatch({ type: 'SELECT_ENDPOINT', endpoint }), []);

  const setSelectedCategory = useCallback((category: string) =>
    dispatch({ type: 'SET_CATEGORY', category }), []);

  const setSearchTerm    = useCallback((term: string)    => dispatch({ type: 'SET_SEARCH', term }), []);
  const setSelectedVersion = useCallback((version: string) => dispatch({ type: 'SET_VERSION', version }), []);
  const setRequestUrl    = useCallback((url: string)     => dispatch({ type: 'SET_REQUEST_URL', url }), []);
  const setRequestMethod = useCallback((method: string)  => dispatch({ type: 'SET_REQUEST_METHOD', method }), []);
  const setRequestHeaders = useCallback((headers: string) => dispatch({ type: 'SET_REQUEST_HEADERS', headers }), []);
  const setRequestBody   = useCallback((body: string)    => dispatch({ type: 'SET_REQUEST_BODY', body }), []);
  const setSelectedApiKey = useCallback((apiKeyId: string | null) => dispatch({ type: 'SET_API_KEY', apiKeyId }), []);
  const setManualApiToken = useCallback((token: string)  => dispatch({ type: 'SET_MANUAL_TOKEN', token }), []);
  const setParameters    = useCallback((parameters: Record<string, string>) =>
    dispatch({ type: 'SET_PARAMETERS', parameters }), []);
  const setResponse      = useCallback((response: ApiResponse | null) =>
    dispatch({ type: 'SET_RESPONSE', response }), []);
  const setLoading       = useCallback((loading: boolean) => dispatch({ type: 'SET_LOADING', loading }), []);
  const setSidebarOpen   = useCallback((open: boolean)   => dispatch({ type: 'SET_SIDEBAR', open }), []);
  const setActiveSchemaId = useCallback((id: string | null) => dispatch({ type: 'SET_ACTIVE_SCHEMA_ID', id }), []);
  const clearAll         = useCallback(() => dispatch({ type: 'RESET' }), []);

  // ── Send request ──────────────────────────────────────────────────────────

  const sendRequest = useCallback(async () => {
    if (!state.requestUrl) {
      consola.error('No URL provided');
      return;
    }

    abortControllerRef.current?.abort();
    const controller = new AbortController();
    abortControllerRef.current = controller;

    // Single dispatch: loading=true + clear response
    dispatch({ type: 'REQUEST_START' });

    const startTime = Date.now();

    try {
      const headers = parseRequestHeaders(state.requestHeaders);

      let bearerToken: string | null = null;
      if (state.manualApiToken) {
        bearerToken = state.manualApiToken;
      } else if (typeof window !== 'undefined') {
        bearerToken = window.localStorage.getItem('auth_token');
      }

      if (bearerToken) headers['Authorization'] = `Bearer ${bearerToken}`;

      const requestOptions: RequestInit = {
        method: state.requestMethod,
        headers,
        signal: controller.signal,
      };

      if (state.requestBody && state.requestMethod !== 'GET') {
        requestOptions.body = state.requestBody;
      }

      const response = await fetch(state.requestUrl, requestOptions);
      const duration = Date.now() - startTime;
      const responseText = await response.text();

      let responseData: unknown;
      try { responseData = JSON.parse(responseText); }
      catch { responseData = responseText; }

      // Single dispatch: response + loading=false + step='response'
      dispatch({
        type: 'REQUEST_SUCCESS',
        response: {
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries()),
          data: responseData,
          duration,
        },
      });

      consola.success(`${state.requestMethod} ${state.requestUrl} → ${response.status} (${duration}ms)`);
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') return;
      consola.error('Request failed:', error);

      // Single dispatch: error response + loading=false
      dispatch({
        type: 'REQUEST_ERROR',
        response: {
          error: error instanceof Error ? error.message : 'Request failed',
          duration: Date.now() - startTime,
        },
      });
    }
  }, [state.requestUrl, state.requestHeaders, state.manualApiToken, state.requestMethod, state.requestBody]);

  // ── Context value ─────────────────────────────────────────────────────────

  const contextValue: PlaygroundContextType = {
    state,
    config,
    apiKeys,
    apiKeysLoading: isLoadingApiKeys,
    setCurrentStep,
    goToNextStep,
    goToPreviousStep,
    setSelectedEndpoint,
    setSelectedCategory,
    setSearchTerm,
    setSelectedVersion,
    setRequestUrl,
    setRequestMethod,
    setRequestHeaders,
    setRequestBody,
    setSelectedApiKey,
    setManualApiToken,
    setParameters,
    setResponse,
    setLoading,
    setSidebarOpen,
    setActiveSchemaId,
    clearAll,
    sendRequest,
  };

  return <PlaygroundContext.Provider value={contextValue}>{children}</PlaygroundContext.Provider>;
};
