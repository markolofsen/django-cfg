import { renderToString } from 'react-dom/server'
import { describe, expect, it } from 'vitest'

import { GalleryGrid } from './GalleryGrid'

const images = [1, 2, 3].map((n) => ({ id: String(n), src: `https://example.com/${n}.webp`, alt: `photo ${n}` }))

function imgTags(html: string): string[] {
  return html.match(/<img[^>]*>/g) ?? []
}

describe('GalleryGrid server render', () => {
  // The lead tile is the page's LCP: hidden until onLoad, it cannot paint
  // before hydration however early its bytes arrive.
  it('paints the lead tile without waiting for hydration', () => {
    const [lead, second] = imgTags(renderToString(<GalleryGrid images={images} onImageClick={() => {}} />))
    expect(lead).not.toContain('opacity-0')
    expect(lead).toMatch(/fetchPriority="high"/i)
    expect(lead).toContain('loading="eager"')
    expect(second).toContain('opacity-0')
    expect(second).toContain('loading="lazy"')
  })
})
