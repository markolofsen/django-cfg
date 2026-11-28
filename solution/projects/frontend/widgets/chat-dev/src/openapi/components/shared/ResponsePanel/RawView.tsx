'use client';

interface RawViewProps {
    rawText: string;
}

/** Verbatim response body. No parsing, no highlighting — readers
 *  occasionally need to inspect trailing whitespace, escape
 *  sequences, or a payload that accidentally claims one content type
 *  and ships another, and the Pretty view hides some of that. */
export function RawView({ rawText }: RawViewProps) {
    if (!rawText) {
        return (
            <div className="py-10 text-center text-xs text-muted-foreground">
                Empty response body
            </div>
        );
    }
    return (
        <pre className="p-4 text-[11px] font-mono text-foreground/70 whitespace-pre-wrap break-all leading-relaxed">
            {rawText}
        </pre>
    );
}
