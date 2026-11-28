import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import { createManifestMetadata, createViewport } from './manifest';

describe('createViewport', () => {
  it('keeps pinch-zoom by default (no maximumScale, no userScalable)', () => {
    const v = createViewport({ themeColor: '#fff' }) as Record<string, unknown>;
    assert.equal(v.width, 'device-width');
    assert.equal(v.initialScale, 1);
    assert.equal('maximumScale' in v, false);
    assert.equal('userScalable' in v, false);
  });

  it('appLike locks zoom explicitly', () => {
    const v = createViewport({ appLike: true }) as Record<string, unknown>;
    assert.equal(v.maximumScale, 1);
    assert.equal(v.userScalable, false);
  });

  it('viewportFit defaults to cover and can be overridden', () => {
    assert.equal((createViewport({}) as Record<string, unknown>).viewportFit, 'cover');
    assert.equal((createViewport({ viewportFit: 'contain' }) as Record<string, unknown>).viewportFit, 'contain');
  });
});

describe('createManifestMetadata', () => {
  it('is installable on iOS with the chosen status bar style', () => {
    const m = createManifestMetadata({ name: 'App', statusBarStyle: 'black-translucent' });
    assert.equal((m.appleWebApp as { capable: boolean }).capable, true);
    assert.equal((m.appleWebApp as { statusBarStyle: string }).statusBarStyle, 'black-translucent');
  });
});
