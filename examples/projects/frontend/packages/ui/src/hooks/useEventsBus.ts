import { useEffect, useRef } from 'react';

export type FormEvent<T extends string = string, P = any> = {
    type: T;
    payload?: P;
    timestamp?: number;
};

type EventListener<T extends FormEvent> = (event: T) => void;

class EventBus {
    private listeners: Set<EventListener<any>> = new Set();

    publish<T extends FormEvent>(event: T) {
        this.listeners.forEach(listener => listener({
            ...event,
            timestamp: event.timestamp || Date.now(),
        }));
    }

    subscribe<T extends FormEvent>(listener: EventListener<T>) {
        this.listeners.add(listener);
        return () => {
            this.listeners.delete(listener);
        };
    }
}

export const events = new EventBus();

export function useEventListener<T extends string, P>(
    eventType: T,
    handler: (payload: P) => void
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
