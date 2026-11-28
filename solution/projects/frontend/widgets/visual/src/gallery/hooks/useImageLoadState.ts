import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Load and error state for an `<img>` that is server-rendered.
 *
 * A tile that hides its image until `onLoad` fires has a hole in it: the
 * browser starts the fetch as soon as it parses the HTML, long before React
 * hydrates, and a cached or fast image finishes first. React attaches `onLoad`
 * at hydration, so the event it was waiting for has already happened and never
 * comes again. The tile then stays at `opacity-0` with its spinner turning,
 * over an image that is sitting there fully decoded.
 *
 * So the state is also read from the element itself once it exists:
 * `complete && naturalWidth > 0` is a finished image, `complete` with width 0
 * is a broken one. `onLoad` and `onError` still cover the case where the
 * image arrives after hydration.
 *
 * Reads `src` so that a tile whose source changes is re-checked, not just
 * reset.
 */
export function useImageLoadState(src: string | undefined) {
  const ref = useRef<HTMLImageElement>(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    const el = ref.current
    const finished = !!el && !!src && el.complete
    setIsLoaded(finished && el.naturalWidth > 0)
    setHasError(finished && el.naturalWidth === 0)
  }, [src])

  const onLoad = useCallback(() => setIsLoaded(true), [])
  const onError = useCallback(() => setHasError(true), [])

  return { ref, isLoaded, hasError, onLoad, onError }
}
