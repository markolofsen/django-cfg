import type { ReactNode } from 'react'

/**
 * Marker info-card data — the Google-Maps-style card that opens above a pin.
 *
 * This is the FULL, in-app shape. The SERIALIZABLE subset (everything except
 * the function/React parts of `actions`) is what the chat `MapBlock` wire
 * format reuses — see `MarkerCardData` below and `MapBlock.markers[].card`.
 */
export interface MarkerCard {
  /** Primary heading (required). */
  title: string
  /** Supporting copy, clamped to ~3 lines in the default card. */
  description?: string
  /** Image URL rendered as a rounded header (object-cover). */
  image?: string
  /** Small pill above the title (e.g. a category). */
  badge?: string
  /** Action row — buttons/links rendered below the body. */
  actions?: MarkerCardAction[]
}

/**
 * A single action in a card's action row.
 *
 * Provide `href` for a link (renders an `<a>`) OR `onClick` for an in-app
 * callback (renders a `<button>`). `icon`/`onClick` are function/React parts
 * that do NOT cross the chat wire — the serializable subset is href-only.
 */
export interface MarkerCardAction {
  /** Visible label. */
  label: string
  /** Link target → renders an anchor. */
  href?: string
  /** In-app callback → renders a button. Ignored when `href` is set. */
  onClick?: () => void
  /** Optional leading icon. */
  icon?: ReactNode
  /** Button style — maps to ui-core Button variants. */
  variant?: 'default' | 'outline' | 'ghost'
}

// ============================================================================
// Serializable subset — the chat wire shape
// ============================================================================

/**
 * Plain-JSON action — the wire subset of {@link MarkerCardAction}. No
 * `onClick`/`icon` (functions/React don't serialize); links only.
 */
export interface MarkerCardActionData {
  label: string
  href?: string
}

/**
 * Plain-JSON card — the wire subset of {@link MarkerCard}. Strings/URLs only,
 * actions are href-only. Carried by the chat `MapBlock` so a marker can open
 * a card with no host code. Assignable to {@link MarkerCard}.
 */
export interface MarkerCardData {
  title: string
  description?: string
  image?: string
  badge?: string
  actions?: MarkerCardActionData[]
}
