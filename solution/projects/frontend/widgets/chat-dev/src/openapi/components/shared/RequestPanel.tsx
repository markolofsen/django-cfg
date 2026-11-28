'use client';

import { Key, Send, Sparkles, Terminal } from 'lucide-react';
import React, { useCallback, useMemo } from 'react';

import {
    Combobox,
    type ComboboxOption,
    Input,
    Textarea,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { LazyPrettyCode as PrettyCode } from '@djangocfg/widget-kit/pretty-code/lazy';
import { usePlaygroundContext } from '../../context/PlaygroundContext';
import { findApiKeyById, isValidJson, parseRequestHeaders } from '../../utils';
import { resolveAbsolute } from '../../utils/url';
import { BodyFormEditor } from './BodyFormEditor';
import { EndpointResetButton } from './EndpointResetButton';
import {
    CollapsibleSection,
    EmptyState,
    ScrollArea,
    SectionLabel,
    relativePath,
} from './ui';

// ─── Param fields ─────────────────────────────────────────────────────────────

type Param = { name: string; type: string; required: boolean; description?: string };

function ParamFields({ label, params }: { label: string; params: Param[] }) {
    const { state, setParameters } = usePlaygroundContext();

    function handleChange(name: string, value: string) {
        setParameters({ ...state.parameters, [name]: value });
    }

    return (
        <div className="space-y-2">
            <SectionLabel>{label}</SectionLabel>
            <div className="space-y-2">
                {params.map((p) => {
                    const value = state.parameters[p.name] ?? '';
                    const placeholder = p.description || p.name;
                    return (
                        <div key={p.name} className="space-y-1">
                            <div className="flex items-center gap-1.5">
                                <span className="font-mono text-[11px] text-foreground/80">{p.name}</span>
                                {p.required && (
                                    <span className="text-[9px] text-destructive font-bold leading-none">*</span>
                                )}
                                <span className="font-mono text-[10px] text-muted-foreground/50">{p.type}</span>
                            </div>
                            <Input
                                value={value}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                                    handleChange(p.name, e.target.value)
                                }
                                placeholder={placeholder}
                                className="h-8 text-xs font-mono"
                            />
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

// ─── RequestPanel ─────────────────────────────────────────────────────────────

export function RequestPanel() {
    const {
        state,
        apiKeys,
        apiKeysLoading,
        setRequestBody,
        setRequestHeaders,
        setSelectedApiKey,
        setManualApiToken,
    } = usePlaygroundContext();

    // Pre-compute every per-key view-model so the JSX stays a flat
    // render — no boolean math in the markup.
    const apiKeyOptions: ComboboxOption[] = useMemo(
        () =>
            apiKeys.map((k) => ({
                value: k.id,
                label: k.name || 'Unnamed key',
                // Surface the first 8 chars of the secret so the user
                // can tell two similarly-named keys apart at a glance.
                description: k.secret
                    ? `${k.secret.slice(0, 8)}…`
                    : undefined,
            })),
        [apiKeys],
    );
    const hasApiKeys = apiKeyOptions.length > 0;

    const ep = state.selectedEndpoint;

    // ── Data (hooks must not be conditional) ─────────────────────────────────
    const isJsonValid = state.requestBody ? isValidJson(state.requestBody) : true;

    const curlCommand = useMemo(() => {
        if (!state.requestUrl) return '';
        // Resolve to an absolute URL so the snippet is runnable from a
        // shell. The live ``fetch`` inside the playground resolves the
        // relative form itself via the browser; copy-pasting to curl
        // doesn't get that treatment.
        const absoluteUrl = resolveAbsolute(state.requestUrl);
        const apiKey = state.selectedApiKey ? findApiKeyById(apiKeys, state.selectedApiKey) : null;
        const hdrs = parseRequestHeaders(state.requestHeaders);
        if (apiKey) hdrs['X-API-Key'] = apiKey.secret || apiKey.id;
        let cmd = `curl -X ${state.requestMethod} "${absoluteUrl}"`;
        Object.entries(hdrs).forEach(([k, v]) => { cmd += ` \\\n  -H "${k}: ${v}"`; });
        if (state.requestBody && state.requestMethod !== 'GET' && isJsonValid) {
            cmd += ` \\\n  -d '${state.requestBody}'`;
        }
        return cmd;
    }, [state, apiKeys, isJsonValid]);

    const pathParams = useMemo(
        () => ep?.parameters?.filter((p) => ep.path.includes(`{${p.name}}`)) ?? [],
        [ep],
    );
    const queryParams = useMemo(
        () => ep?.parameters?.filter((p) => !ep.path.includes(`{${p.name}}`)) ?? [],
        [ep],
    );

    // ── Derived ───────────────────────────────────────────────────────────────
    // Show the absolute URL in the meta row so the user sees exactly
    // what will go over the wire — same rewrite we do for cURL.
    const displayUrl     = resolveAbsolute(state.requestUrl || ep?.path || '');
    const hasBody        = ep?.method !== 'GET';
    const bodyType       = ep?.requestBody?.type ?? '';
    const hasPathParams  = pathParams.length > 0;
    const hasQueryParams = queryParams.length > 0;
    const hasCurl        = Boolean(curlCommand);
    const epPath         = ep ? relativePath(ep.path) : '';
    // Show the URL meta row only when it differs from the endpoint's
    // template shape — i.e. the user has substituted path params or the
    // URL host is worth showing explicitly.
    const urlChanged     = displayUrl !== '' && displayUrl !== epPath;

    // ── Early return ──────────────────────────────────────────────────────────
    if (!ep) {
        return <EmptyState icon={Send} text="Select an endpoint to build a request" />;
    }

    // ── Render ────────────────────────────────────────────────────────────────
    return (
        <>
            {/* Inline meta row — shows the effective URL when it differs
                from the endpoint's path template (e.g. after substituting
                path parameters), plus the Reset action. We dropped the
                full endpoint header because the containing surface (SidePanel
                in docs layout, column header in classic layout) already
                shows the method + path, and duplicating the Send button
                next to a full-width Send at the bottom read as confusing. */}
            {(urlChanged || ep) && (
                <div className="shrink-0 border-b px-4 py-2 bg-muted/10 flex items-center gap-2 min-h-[28px]">
                    {urlChanged ? (
                        <span className="font-mono text-[10px] text-muted-foreground/60 break-all leading-snug truncate min-w-0 flex-1">
                            {displayUrl}
                        </span>
                    ) : (
                        <span className="flex-1" />
                    )}
                    <EndpointResetButton />
                </div>
            )}

            {/* Scrollable fields */}
            <ScrollArea className="px-4 py-3 space-y-3">

                {hasPathParams  && <ParamFields label="Path Parameters"  params={pathParams} />}
                {hasQueryParams && <ParamFields label="Query Parameters" params={queryParams} />}

                {/* Body */}
                {hasBody && (
                    <BodySection
                        schema={ep.requestBody?.schema}
                        bodyType={bodyType}
                        bodyDescription={ep.requestBody?.description}
                        value={state.requestBody}
                        onChange={setRequestBody}
                        isJsonValid={isJsonValid}
                    />
                )}

                {/* Auth & Headers — collapsed by default */}
                <CollapsibleSection
                    label={
                        <span className="inline-flex items-center gap-1">
                            <Key className="h-2.5 w-2.5" />
                            Auth &amp; Headers
                        </span>
                    }
                >
                    <div className="space-y-3 pt-2">
                        <div className="space-y-1.5">
                            <SectionLabel>API Key</SectionLabel>
                            <Combobox
                                options={apiKeyOptions}
                                value={state.selectedApiKey ?? ''}
                                onValueChange={(v) => setSelectedApiKey(v || null)}
                                placeholder={
                                    apiKeysLoading
                                        ? 'Loading keys…'
                                        : hasApiKeys
                                            ? 'Select an API key'
                                            : 'No API keys yet'
                                }
                                searchPlaceholder="Search keys…"
                                emptyText="No matching key"
                                disabled={apiKeysLoading || !hasApiKeys}
                                className="h-8"
                            />
                            <p className="text-[10px] text-muted-foreground">
                                Picks are sent via the{' '}
                                <span className="font-mono">X-API-Key</span> header.
                            </p>
                        </div>
                        <div className="space-y-1.5">
                            <SectionLabel>Bearer Token</SectionLabel>
                            <Input
                                type="password"
                                placeholder="Leave empty to use JWT from localStorage"
                                value={state.manualApiToken}
                                onChange={(e) => setManualApiToken(e.target.value)}
                                className="font-mono text-xs h-8"
                            />
                        </div>
                        <div className="space-y-1.5">
                            <SectionLabel>Headers</SectionLabel>
                            <Textarea
                                value={state.requestHeaders}
                                onChange={(e) => setRequestHeaders(e.target.value)}
                                className="font-mono text-[11px] min-h-[60px] resize-y"
                                rows={3}
                            />
                        </div>
                    </div>
                </CollapsibleSection>

                {/* cURL — collapsed by default. PrettyCode has its own
                    hover-toolbar with Copy, so no duplicate action here. */}
                {hasCurl && (
                    <CollapsibleSection
                        label={
                            <span className="inline-flex items-center gap-1">
                                <Terminal className="h-2.5 w-2.5" />
                                cURL
                            </span>
                        }
                    >
                        <div className="mt-2">
                            <PrettyCode
                                data={curlCommand}
                                language="bash"
                                isCompact
                                maxLines={50}
                            />
                        </div>
                    </CollapsibleSection>
                )}

                {/* Bottom breathing room — the Send footer lives outside
                    this component (in SlideInPlayground / TryItSheet),
                    so we just leave a little space so the last section
                    doesn't crash against the container edge. */}
                <div className="h-4" />
            </ScrollArea>
        </>
    );
}

// ─── Body section ─────────────────────────────────────────────────────────────

interface BodySectionProps {
    schema: Record<string, unknown> | undefined;
    bodyType: string;
    bodyDescription?: string;
    /** JSON-serialised body kept in context. Form edits are re-serialised
     *  before being written back so one source of truth survives across
     *  the two view modes. */
    value: string;
    onChange: (raw: string) => void;
    isJsonValid: boolean;
}

type BodyViewMode = 'form' | 'json';

function BodySection({ schema, bodyType, bodyDescription, value, onChange, isJsonValid }: BodySectionProps) {
    // Default to form view when we have a schema to drive it. Fall back
    // to raw JSON for schemaless endpoints (or binary bodies, etc.).
    const hasSchema = !!schema;
    const [mode, setMode] = React.useState<BodyViewMode>(hasSchema ? 'form' : 'json');

    // Parse the context's JSON string once per value change so the form
    // sees a structured object. Invalid JSON is tolerated — the form
    // simply shows empty fields until the user fixes it.
    const parsed = React.useMemo(() => {
        if (!value) return null;
        try { return JSON.parse(value); } catch { return null; }
    }, [value]);

    const handleFormChange = useCallback(
        (next: unknown) => {
            onChange(JSON.stringify(next, null, 2));
        },
        [onChange],
    );

    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between gap-2 flex-wrap">
                <div className="flex items-baseline gap-2 min-w-0">
                    <SectionLabel>Body</SectionLabel>
                    {bodyType && (
                        <span className="text-[10px] text-muted-foreground/40 font-mono">{bodyType}</span>
                    )}
                    {bodyDescription && (
                        <span className="text-[10px] text-muted-foreground/60 truncate">{bodyDescription}</span>
                    )}
                </div>
                {hasSchema && (
                    <div className="inline-flex rounded-md border overflow-hidden text-[10px]">
                        <ModeButton active={mode === 'form'} onClick={() => setMode('form')}>Form</ModeButton>
                        <ModeButton active={mode === 'json'} onClick={() => setMode('json')}>JSON</ModeButton>
                    </div>
                )}
                {mode === 'json' && isJsonValid && value && (
                    <button
                        type="button"
                        onClick={() => {
                            try { onChange(JSON.stringify(JSON.parse(value), null, 2)); } catch { /* noop */ }
                        }}
                        className="inline-flex items-center gap-1 text-[10px] text-muted-foreground hover:text-foreground transition-colors"
                    >
                        <Sparkles className="h-2.5 w-2.5" />
                        Format
                    </button>
                )}
            </div>

            {mode === 'form' && hasSchema ? (
                <BodyFormEditor
                    schema={schema as Record<string, unknown>}
                    value={parsed}
                    onChange={handleFormChange}
                />
            ) : (
                <>
                    <Textarea
                        placeholder={'{\n  "key": "value"\n}'}
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        className={cn(
                            'font-mono text-[11px] min-h-[90px] resize-y',
                            !isJsonValid && 'border-destructive focus-visible:ring-destructive/30',
                        )}
                        rows={4}
                    />
                    {!isJsonValid && <p className="text-[10px] text-destructive">Invalid JSON</p>}
                </>
            )}
        </div>
    );
}

function ModeButton({
    active, onClick, children,
}: {
    active: boolean;
    onClick: () => void;
    children: React.ReactNode;
}) {
    return (
        <button
            type="button"
            onClick={onClick}
            className={cn(
                'px-2 py-0.5 font-medium transition-colors',
                active
                    ? 'bg-primary/10 text-foreground'
                    : 'text-muted-foreground hover:text-foreground',
            )}
        >
            {children}
        </button>
    );
}
