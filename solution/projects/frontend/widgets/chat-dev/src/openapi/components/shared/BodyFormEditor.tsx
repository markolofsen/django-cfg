'use client';

/**
 * Form-based request body editor driven by JSON Schema.
 *
 * Replaces the ``{"key":"value"}`` textarea prompt with a real form:
 * one input per property, typed widgets for primitives, nested objects
 * indented, arrays with add/remove. The component is controlled — the
 * parent owns the body value (as any JSON) and persists to localStorage.
 *
 * Intentionally not a full JSON-Schema-Form: we don't cover oneOf/anyOf,
 * pattern validation, min/max — the playground just needs a usable
 * interactive shape. Users who hit a corner case can flip the ``JSON``
 * toggle in RequestPanel and edit raw.
 */

import { Minus, Plus } from 'lucide-react';
import React, { useCallback, useMemo } from 'react';

import { Combobox, Input, Switch, Textarea } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { SectionLabel } from './ui';

type JsonSchemaNode = Record<string, unknown> & {
    type?: string;
    properties?: Record<string, JsonSchemaNode>;
    required?: string[];
    items?: JsonSchemaNode;
    enum?: unknown[];
    description?: string;
    format?: string;
};

const MAX_DEPTH = 6;

// ─── Value helpers ────────────────────────────────────────────────────────────

function defaultForSchema(schema: JsonSchemaNode | undefined): unknown {
    if (!schema) return null;
    if (Array.isArray(schema.enum) && schema.enum.length > 0) return schema.enum[0];
    switch (schema.type) {
        case 'object': {
            const out: Record<string, unknown> = {};
            for (const [k, v] of Object.entries(schema.properties ?? {})) {
                out[k] = defaultForSchema(v);
            }
            return out;
        }
        case 'array':
            return [];
        case 'integer':
        case 'number':
            return 0;
        case 'boolean':
            return false;
        case 'string':
            return '';
        default:
            if (schema.properties) {
                const out: Record<string, unknown> = {};
                for (const [k, v] of Object.entries(schema.properties)) {
                    out[k] = defaultForSchema(v);
                }
                return out;
            }
            return '';
    }
}

// ─── Root ─────────────────────────────────────────────────────────────────────

export interface BodyFormEditorProps {
    schema: JsonSchemaNode;
    value: unknown;
    onChange: (next: unknown) => void;
}

export function BodyFormEditor({ schema, value, onChange }: BodyFormEditorProps) {
    return (
        <SchemaField
            schema={schema}
            value={value}
            onChange={onChange}
            depth={0}
            required={false}
        />
    );
}

// ─── Recursive renderer ───────────────────────────────────────────────────────

interface SchemaFieldProps {
    schema: JsonSchemaNode;
    value: unknown;
    onChange: (next: unknown) => void;
    depth: number;
    required: boolean;
    label?: string;
}

function SchemaField({ schema, value, onChange, depth, required, label }: SchemaFieldProps) {
    // Depth cutoff: collapse further nesting into a raw JSON textarea —
    // deeper forms get impossible to navigate and lose value for the UX
    // we're trying to offer (quick exploration).
    if (depth > MAX_DEPTH) {
        return <RawJsonField label={label} value={value} onChange={onChange} />;
    }

    if (Array.isArray(schema.enum) && schema.enum.length > 0) {
        return <EnumField schema={schema} value={value} onChange={onChange} label={label} required={required} />;
    }

    switch (schema.type) {
        case 'object':
            return <ObjectField schema={schema} value={value} onChange={onChange} depth={depth} label={label} />;
        case 'array':
            return <ArrayField schema={schema} value={value} onChange={onChange} depth={depth} label={label} required={required} />;
        case 'boolean':
            return <BooleanField value={value} onChange={onChange} label={label} schema={schema} required={required} />;
        case 'integer':
        case 'number':
            return <NumberField value={value} onChange={onChange} label={label} schema={schema} required={required} />;
        case 'string':
        default:
            // Untyped / string-ish — plain text input. Covers the
            // "body is a free-form string" case too (e.g. text/plain).
            if (!schema.type && schema.properties) {
                return <ObjectField schema={schema} value={value} onChange={onChange} depth={depth} label={label} />;
            }
            return <StringField value={value} onChange={onChange} label={label} schema={schema} required={required} />;
    }
}

// ─── Primitive widgets ────────────────────────────────────────────────────────

function FieldHeader({
    label,
    type,
    required,
    description,
}: {
    label?: string;
    type: string;
    required: boolean;
    description?: string;
}) {
    if (!label) return null;
    return (
        <div className="space-y-0.5">
            <div className="flex items-baseline gap-1.5">
                <span className="font-mono text-[11px] text-foreground/80">{label}</span>
                {required && <span className="text-[9px] text-destructive font-bold leading-none">*</span>}
                <span className="font-mono text-[10px] text-muted-foreground/50">{type}</span>
            </div>
            {description && (
                <p className="text-[10px] text-muted-foreground/70 leading-snug">{description}</p>
            )}
        </div>
    );
}

function StringField({
    value, onChange, label, schema, required,
}: {
    value: unknown;
    onChange: (next: string) => void;
    label?: string;
    schema: JsonSchemaNode;
    required: boolean;
}) {
    const stringValue = typeof value === 'string' ? value : value == null ? '' : String(value);
    const placeholder = schema.format ? `${schema.type ?? 'string'} (${schema.format})` : schema.description || schema.type || 'string';
    return (
        <div className="space-y-1">
            <FieldHeader label={label} type={schema.format ? `string (${schema.format})` : 'string'} required={required} description={schema.description} />
            <Input
                value={stringValue}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                className="h-8 text-xs font-mono"
            />
        </div>
    );
}

function NumberField({
    value, onChange, label, schema, required,
}: {
    value: unknown;
    onChange: (next: number | null) => void;
    label?: string;
    schema: JsonSchemaNode;
    required: boolean;
}) {
    const raw = value == null ? '' : String(value);
    const type = schema.type === 'integer' ? 'integer' : 'number';
    return (
        <div className="space-y-1">
            <FieldHeader label={label} type={schema.format ? `${type} (${schema.format})` : type} required={required} description={schema.description} />
            <Input
                type="number"
                value={raw}
                onChange={(e) => {
                    const v = e.target.value;
                    if (v === '') return onChange(null);
                    const n = schema.type === 'integer' ? parseInt(v, 10) : parseFloat(v);
                    onChange(Number.isNaN(n) ? null : n);
                }}
                placeholder={type}
                className="h-8 text-xs font-mono"
            />
        </div>
    );
}

function BooleanField({
    value, onChange, label, schema, required,
}: {
    value: unknown;
    onChange: (next: boolean) => void;
    label?: string;
    schema: JsonSchemaNode;
    required: boolean;
}) {
    const bool = value === true;
    return (
        <div className="flex items-start justify-between gap-3">
            <FieldHeader label={label} type="boolean" required={required} description={schema.description} />
            <Switch checked={bool} onCheckedChange={onChange} className="mt-0.5 shrink-0" />
        </div>
    );
}

function EnumField({
    schema, value, onChange, label, required,
}: {
    schema: JsonSchemaNode;
    value: unknown;
    onChange: (next: unknown) => void;
    label?: string;
    required: boolean;
}) {
    const options = (schema.enum ?? []).map((v) => ({
        value: String(v),
        label: String(v),
    }));
    const strValue = value == null ? '' : String(value);
    return (
        <div className="space-y-1">
            <FieldHeader label={label} type={`${schema.type ?? 'enum'} enum`} required={required} description={schema.description} />
            <Combobox
                options={options}
                value={strValue}
                onValueChange={(v) => {
                    // Preserve original type if schema declares integer/number.
                    if (schema.type === 'integer') onChange(parseInt(v, 10));
                    else if (schema.type === 'number') onChange(parseFloat(v));
                    else onChange(v);
                }}
                placeholder="Select…"
                searchPlaceholder="Search…"
                className="h-8 text-xs"
            />
        </div>
    );
}

function RawJsonField({
    label, value, onChange,
}: {
    label?: string;
    value: unknown;
    onChange: (next: unknown) => void;
}) {
    const [text, setText] = React.useState(() => JSON.stringify(value ?? null, null, 2));
    // Resync when value changes from outside (e.g. endpoint switch).
    React.useEffect(() => {
        setText(JSON.stringify(value ?? null, null, 2));
    }, [value]);
    return (
        <div className="space-y-1">
            {label && <SectionLabel>{label} (raw)</SectionLabel>}
            <Textarea
                value={text}
                onChange={(e) => {
                    setText(e.target.value);
                    try { onChange(JSON.parse(e.target.value)); } catch { /* keep last valid */ }
                }}
                className="font-mono text-[11px] min-h-[80px]"
                rows={4}
            />
        </div>
    );
}

// ─── Composite widgets ────────────────────────────────────────────────────────

function ObjectField({
    schema, value, onChange, depth, label,
}: {
    schema: JsonSchemaNode;
    value: unknown;
    onChange: (next: Record<string, unknown>) => void;
    depth: number;
    label?: string;
}) {
    // Memoised so the `{}` fallback is not a fresh reference each render, which
    // would rebuild every field's `setKey` handler.
    const obj = useMemo(
        () =>
            value && typeof value === 'object' && !Array.isArray(value)
                ? (value as Record<string, unknown>)
                : {},
        [value],
    );
    const required = new Set(schema.required ?? []);
    const entries = Object.entries(schema.properties ?? {});

    const setKey = useCallback(
        (key: string) => (next: unknown) => {
            onChange({ ...obj, [key]: next });
        },
        [obj, onChange],
    );

    if (entries.length === 0) {
        return <RawJsonField label={label} value={obj} onChange={onChange as (v: unknown) => void} />;
    }

    // Root-level object (depth === 0) renders flat; nested gets an
    // indented, bordered group so the hierarchy is visible.
    const wrapperClass = depth === 0
        ? 'space-y-3'
        : 'space-y-2 border-l-2 border-border/60 pl-3 ml-px';

    return (
        <div className="space-y-1.5">
            {label && depth > 0 && (
                <div className="flex items-baseline gap-1.5">
                    <span className="font-mono text-[11px] text-foreground/80">{label}</span>
                    <span className="font-mono text-[10px] text-muted-foreground/50">object</span>
                </div>
            )}
            <div className={cn(wrapperClass)}>
                {entries.map(([key, subSchema]) => (
                    <SchemaField
                        key={key}
                        schema={subSchema}
                        value={obj[key]}
                        onChange={setKey(key)}
                        depth={depth + 1}
                        required={required.has(key)}
                        label={key}
                    />
                ))}
            </div>
        </div>
    );
}

function ArrayField({
    schema, value, onChange, depth, label, required,
}: {
    schema: JsonSchemaNode;
    value: unknown;
    onChange: (next: unknown[]) => void;
    depth: number;
    label?: string;
    required: boolean;
}) {
    const arr = Array.isArray(value) ? value : [];
    const items = schema.items ?? { type: 'string' };

    const addItem = () => onChange([...arr, defaultForSchema(items)]);
    const removeAt = (i: number) => onChange(arr.filter((_, idx) => idx !== i));
    const setAt = (i: number) => (next: unknown) =>
        onChange(arr.map((v, idx) => (idx === i ? next : v)));

    return (
        <div className="space-y-1.5">
            {label && (
                <div className="flex items-baseline gap-1.5">
                    <span className="font-mono text-[11px] text-foreground/80">{label}</span>
                    {required && <span className="text-[9px] text-destructive font-bold leading-none">*</span>}
                    <span className="font-mono text-[10px] text-muted-foreground/50">
                        {`array<${items.type ?? 'any'}>`}
                    </span>
                </div>
            )}
            <div className="space-y-2 border-l-2 border-border/60 pl-3 ml-px">
                {arr.length === 0 && (
                    <p className="text-[10px] text-muted-foreground/50 italic">Empty array</p>
                )}
                {arr.map((v, i) => (
                    <div key={i} className="flex items-start gap-2">
                        <div className="flex-1 min-w-0">
                            <SchemaField
                                schema={items}
                                value={v}
                                onChange={setAt(i)}
                                depth={depth + 1}
                                required={false}
                                label={`${label ?? ''}[${i}]`}
                            />
                        </div>
                        <button
                            type="button"
                            onClick={() => removeAt(i)}
                            title="Remove item"
                            className="shrink-0 h-7 w-7 inline-flex items-center justify-center rounded-md text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                        >
                            <Minus className="h-3.5 w-3.5" />
                        </button>
                    </div>
                ))}
                <button
                    type="button"
                    onClick={addItem}
                    className="inline-flex items-center gap-1.5 text-[10px] text-muted-foreground hover:text-foreground transition-colors py-1"
                >
                    <Plus className="h-3 w-3" />
                    Add item
                </button>
            </div>
        </div>
    );
}
