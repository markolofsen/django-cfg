'use client';

/**
 * The EAGER entry: the root surface with `MapContainer` imported STATICALLY
 * rather than behind `React.lazy`.
 *
 * For the one case the lazy default reads badly — the map IS the page, and a
 * placeholder is a flash rather than a courtesy. Importing this alongside the
 * root in one app defeats the split: a static edge pulls MapLibre into the
 * entry chunk whatever the other half does.
 *
 * Derived from the root rather than restated. The two used to be hand-kept
 * lists and had drifted 16 symbols apart in one direction and 36 in the other
 * — a consumer's import resolving or not came down to which entry it named.
 */

export * from './index';

// The whole difference: the container as a static edge.
export { MapContainer, MapView } from './components/MapContainer';
