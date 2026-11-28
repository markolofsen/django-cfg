/**
 * Register extra Prism language grammars onto the vendored Prism
 * instance that ``prism-react-renderer`` ships.
 *
 *  Why this file exists:
 *    ``prism-react-renderer@2.x`` bundles only a small set of core
 *    languages (javascript, typescript, python, go, json, css,
 *    markup, clike, …). Anything else — ``bash``, ``ruby``, ``java``,
 *    ``php`` — isn't in the bundle, so passing ``language="bash"`` to
 *    ``<Highlight>`` silently renders as plain text.
 *
 *  Canonical solution (per the official README):
 *    - Grab the exported ``Prism`` instance.
 *    - Hang it off ``globalThis`` so that ``prismjs`` language
 *      components can find it when they self-register (they read
 *      ``window.Prism`` / ``global.Prism`` at module-evaluation time).
 *    - Load each grammar via dynamic ``import()`` — bare ``require``
 *      doesn't work in ESM/Vite and static ``import 'prismjs/…'``
 *      runs before we can hang Prism on the global.
 *
 *  Loading starts when the first block renders (`useEnsurePrismLanguages`),
 *  not at import: a host that mounts the chat but never shows code must not
 *  fetch four grammars. Repeated calls share one promise. Safe for SSR: the grammars don't
 *  touch the DOM and the dynamic import is awaited asynchronously —
 *  server renders just miss the extra grammars, client renders pick
 *  them up after hydration which is when the <Highlight> components
 *  actually render anyway.
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

import { useSyncExternalStore } from 'react';
import { Prism } from 'prism-react-renderer';

// Hang the vendored Prism on the global so ``prismjs`` language
// components can find it when their self-registration runs.
const globalScope: any = typeof globalThis !== 'undefined' ? globalThis : {};
if (!globalScope.Prism) {
    globalScope.Prism = Prism;
}

// Ready-state machinery: one-shot boolean + subscribers. When loading
// finishes we flip ``ready`` and notify listeners so components that
// rendered before the grammars loaded can re-render and pick them up.
let ready = false;
let loading: Promise<void> | null = null;
const listeners = new Set<() => void>();

function subscribe(cb: () => void): () => void {
    listeners.add(cb);
    return () => listeners.delete(cb);
}

function getSnapshot(): boolean {
    return ready;
}

// Server snapshot — always ``true`` so SSR doesn't trip the
// ``server ≠ client`` warning. The actual registration only runs on
// the client; server renders fall back to the bundled Prism set,
// which for the OpenAPI viewer means JS / Python / Go highlight
// server-side and bash / java / ruby / php render plain until hydration.
function getServerSnapshot(): boolean {
    return true;
}

export async function ensurePrismLanguages(): Promise<void> {
    if (ready) return;
    if (loading) return loading;

    loading = (async () => {
        // Dynamic imports so these modules evaluate AFTER we've
        // attached Prism to the global scope above.
        //
        // `as string` because the grammar files are untyped side-effect
        // modules — `prismjs` ships no declarations for `components/*` and
        // there is no `@types/prismjs` here. It widens the specifier, not a
        // value, so nothing about the loaded module is being asserted.
        //
        // Load order matters: ``prism-php`` calls
        // ``Prism.languages.markup.tokenizePlaceholders`` at module
        // evaluation time, which is only defined after
        // ``markup-templating`` loads — so that must come first.
        // ``bash`` / ``java`` / ``ruby`` only depend on ``clike``
        // which is already bundled in ``prism-react-renderer``.
        await import('prismjs/components/prism-markup-templating' as string);
        await Promise.all([
            import('prismjs/components/prism-bash' as string),
            import('prismjs/components/prism-java' as string),
            import('prismjs/components/prism-ruby' as string),
            import('prismjs/components/prism-php' as string),
        ]);
        ready = true;
        listeners.forEach((cb) => cb());
    })();

    return loading;
}

/** Hook that triggers a re-render when the extra grammars finish
 *  loading. Used by ``PrettyCode`` and the diff viewer so the first render (which might
 *  happen before loading completes) gets re-highlighted once the
 *  grammars are available. */
export function useEnsurePrismLanguages(): boolean {
    const loaded = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
    if (!loaded) {
        // Kick off loading (idempotent — re-entry is cheap) so the
        // next store update flips ``ready`` and we re-render.
        void ensurePrismLanguages();
    }
    return loaded;
}
