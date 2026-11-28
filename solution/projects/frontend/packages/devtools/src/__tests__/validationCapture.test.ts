// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';

const { capture } = vi.hoisted(() => ({ capture: vi.fn() }));
vi.mock('../store', () => ({ devtoolsStore: { getState: () => ({ capture }) } }));

import { installConsoleCapture, installValidationCapture, installNetworkCapture } from '../capture';

describe('generated-client validation reporting', () => {
  afterEach(() => {
    capture.mockClear();
    vi.restoreAllMocks();
  });

  it('keeps the console diagnostic visible and ingests the structured event once', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const stopConsole = installConsoleCapture();
    const stopValidation = installValidationCapture();
    try {
      console.error('[DjangoCFG:validation] ERR-12345 GET /apix/test/: slug: invalid_format');
      expect(consoleSpy).toHaveBeenCalledTimes(1);
      expect(capture).not.toHaveBeenCalled();

      window.dispatchEvent(new CustomEvent('zod-validation-error', {
        detail: {
          operation: 'GET /apix/test/', method: 'GET', path: '/apix/test/',
          reference: 'ERR-12345',
          diagnostic: 'slug: invalid_format',
          error: { message: 'private raw response value' },
        },
      }));
      expect(capture).toHaveBeenCalledTimes(1);
      expect(capture.mock.calls[0]?.[0]).toMatchObject({
        http_method: 'GET', http_url: '/apix/test/',
        extra: { reference: 'ERR-12345' },
      });
      expect(capture.mock.calls[0]?.[0].message).toContain('slug: invalid_format');
      expect(JSON.stringify(capture.mock.calls[0])).not.toContain('private raw response value');
    } finally {
      stopValidation();
      stopConsole();
    }
  });
});

describe('generated-client network reporting', () => {
  afterEach(() => {
    capture.mockClear();
    vi.restoreAllMocks();
  });

  it('does not ingest console-only refusals and captures a network event once', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const error = vi.spyOn(console, 'error').mockImplementation(() => {});
    const stopConsole = installConsoleCapture();
    const stopNetwork = installNetworkCapture();
    try {
      console.warn('[DjangoCFG:request] ERR-ONE POST /apix/test/: HTTP 400');
      console.error('[DjangoCFG:request] ERR-TWO GET /apix/test/: HTTP 503');
      expect(warn).toHaveBeenCalledTimes(1);
      expect(error).toHaveBeenCalledTimes(1);
      expect(capture).not.toHaveBeenCalled();

      window.dispatchEvent(new CustomEvent('network-error', {
        detail: { method: 'GET', url: '/apix/test/', error: 'HTTP 503',
                  statusCode: 503, reference: 'ERR-TWO' },
      }));
      expect(capture).toHaveBeenCalledTimes(1);
      expect(capture.mock.calls[0]?.[0]).toMatchObject({
        http_method: 'GET', http_url: '/apix/test/', http_status: 503,
        extra: { reference: 'ERR-TWO' },
      });
      window.dispatchEvent(new CustomEvent('network-error', {
        detail: { method: 'POST', url: '/cfg/monitor/ingest/', error: 'Network request failed' },
      }));
      expect(capture).toHaveBeenCalledTimes(1);
    } finally {
      stopNetwork();
      stopConsole();
    }
  });
});
