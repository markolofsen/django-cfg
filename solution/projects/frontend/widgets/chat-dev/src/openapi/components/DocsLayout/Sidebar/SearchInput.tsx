'use client';

import { Search, X } from 'lucide-react';
import React from 'react';

import { Input } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

interface SearchInputProps {
    value: string;
    onChange: (v: string) => void;
    placeholder?: string;
}

/** Search field with a leading icon and a trailing clear button. The
 *  clear button only appears when there's something to clear so the
 *  idle state reads as a single clean input rather than "icon + input
 *  + mystery button". */
export function SearchInput({ value, onChange, placeholder }: SearchInputProps) {
    return (
        <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground/50 pointer-events-none" />
            <Input
                placeholder={placeholder ?? 'Search endpoints…'}
                value={value}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
                className="pl-8 pr-7 h-8 text-xs"
            />
            {value && (
                <button
                    type="button"
                    onClick={() => onChange('')}
                    aria-label="Clear search"
                    className={cn(
                        'absolute right-1.5 top-1/2 -translate-y-1/2 h-5 w-5 rounded',
                        'inline-flex items-center justify-center',
                        'text-muted-foreground/50 hover:text-foreground hover:bg-muted transition-colors',
                    )}
                >
                    <X className="h-3 w-3" />
                </button>
            )}
        </div>
    );
}
