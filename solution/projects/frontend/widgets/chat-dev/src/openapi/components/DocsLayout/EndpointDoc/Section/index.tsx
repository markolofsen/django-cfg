'use client';

import React from 'react';

import { useEndpointDocContext } from '../context';
import { useEndpointDocStore } from '../store';
import { useIsSectionOpen } from '../store/selectors';
import type { SectionId } from '../types';
import { defaultSectionOpen } from './defaults';
import { SectionHeader } from './SectionHeader';

interface SectionProps {
    /** Identifies the section inside the endpoint's card — used as a
     *  key in zustand + URL hash routing. Must match one of ``SectionId``. */
    id: SectionId;
    title: string;
    /** Optional count badge shown next to the title. */
    badge?: number;
    children: React.ReactNode;
}

/** Collapsible section wrapper. Pulls endpoint identity from
 *  ``EndpointDocProvider`` so the component API stays at "id + title"
 *  — the rest is implicit from context. Children render lazily when
 *  open; a docs page may mount dozens of endpoints × four sections and
 *  mounting everything eagerly would churn on the first scroll pass. */
export function Section({ id, title, badge, children }: SectionProps) {
    const { endpointId, method } = useEndpointDocContext();
    const defaultOpen = defaultSectionOpen(method, id);
    const open = useIsSectionOpen(endpointId, id, defaultOpen);
    const toggleSection = useEndpointDocStore((s) => s.toggleSection);

    return (
        <div className="space-y-2.5">
            <SectionHeader
                sectionId={id}
                title={title}
                badge={badge}
                open={open}
                onToggle={() => toggleSection(endpointId, id, defaultOpen)}
            />
            {open && <div>{children}</div>}
        </div>
    );
}
