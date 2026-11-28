/**
 * Shared ground for the widgets. Nothing lands here on the strength of looking
 * reusable — a SECOND consumer is the entry price, because a one-consumer
 * helper in a shared package is a helper in the wrong package.
 *
 * A widget may depend on this. This may depend on no widget.
 *
 * `./lazy` is deliberately NOT re-exported here: it is React and pulls
 * `@djangocfg/ui-core` behind it, and this root is pure — a consumer wanting
 * `formatBytes` must not pay for a component tree. Import it by its subpath.
 */
export * from './format';
