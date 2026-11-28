// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, describe, expect, it, vi } from 'vitest';

const { showError } = vi.hoisted(() => ({ showError: vi.fn() }));
vi.mock('@djangocfg/ui-core/hooks', () => ({ toast: { error: showError } }));
vi.mock('@djangocfg/devtools', () => ({
  useDebugMode: () => false,
  isProduction: true,
  EventType: { ERROR: 'error', NETWORK_ERROR: 'network_error', JS_ERROR: 'js_error' },
  EventLevel: { WARNING: 'warning', ERROR: 'error' },
}));
vi.mock('../components/ErrorToast', () => ({ createErrorToast: vi.fn() }));

import { ErrorTrackingProvider } from './ErrorTrackingProvider';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

describe('production diagnostic references', () => {
  afterEach(() => showError.mockClear());

  it('uses the exact runtime reference in the safe validation and network toasts', () => {
    const host = document.createElement('div');
    const root = createRoot(host);
    act(() => root.render(<ErrorTrackingProvider><div /></ErrorTrackingProvider>));
    try {
      act(() => window.dispatchEvent(new CustomEvent('zod-validation-error', {
        detail: {
          operation: 'GET /test/', method: 'GET', path: '/test/',
          reference: 'ERR-VALIDATION', error: { issues: [{ code: 'invalid_type', path: ['ok'], message: 'private' }] },
          response: { ok: 'private' }, timestamp: new Date(),
        },
      })));
      expect(showError).toHaveBeenCalledWith('Invalid data received', expect.objectContaining({
        description: 'Please try again. Reference: ERR-VALIDATION',
      }));

      act(() => window.dispatchEvent(new CustomEvent('network-error', {
        detail: { method: 'POST', url: '/test/', reference: 'ERR-NETWORK',
                  statusCode: 503, error: 'HTTP 503', timestamp: new Date() },
      })));
      expect(showError).toHaveBeenCalledWith('Server error', expect.objectContaining({
        description: "We're working on it. Reference: ERR-NETWORK",
      }));
      expect(showError).toHaveBeenCalledTimes(2);
    } finally {
      act(() => root.unmount());
    }
  });
});
