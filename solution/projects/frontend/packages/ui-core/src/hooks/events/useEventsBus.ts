'use client';

import { useEffect, useRef } from 'react';

export type FormEvent<T extends string = string, P = unknown> = {
    type: T;
    payload?: P;
    timestamp?: number;
};

type EventListener<T extends FormEvent> = (event: T) => void;

class EventBus {
    // Subscribers each declare their own event type; the bus only ever hands
    // them a FormEvent, so it stores the widest listener it can actually call.
    private listeners: Set<EventListener<FormEvent>> = new Set();

    publish<T extends FormEvent>(event: T) {
        this.listeners.forEach(listener => listener({
            ...event,
            timestamp: event.timestamp || Date.now(),
        }));
    }

    // Not generic on purpose: the bus broadcasts EVERY event to EVERY listener,
    // so a listener declaring a narrower event type would be handed events that
    // do not match it. Filtering by `type` is the subscriber's job.
    subscribe(listener: EventListener<FormEvent>) {
        this.listeners.add(listener);
        return () => {
            this.listeners.delete(listener);
        };
    }
}

export const events = new EventBus();

/**
 * Subscribe to one event type on the bus.
 *
 * The payload arrives from an untyped publisher, so it is delivered as
 * `unknown`: this is the boundary, and the handler narrows it. Callers that
 * know the publisher's shape should narrow with a type guard rather than
 * declaring the shape and hoping — nothing at runtime enforces the pairing of
 * `eventType` and payload.
 */
export function useEventListener<T extends string>(
    eventType: T,
    handler: (payload: unknown) => void
) {
    const savedHandler = useRef(handler);

    useEffect(() => {
        savedHandler.current = handler;
    }, [handler]);

    useEffect(() => {
        const listener = (event: FormEvent) => {
            if (event.type === eventType) {
                savedHandler.current(event.payload);
            }
        };

        const unsubscribe = events.subscribe(listener);
        return () => unsubscribe();
    }, [eventType]);
}
