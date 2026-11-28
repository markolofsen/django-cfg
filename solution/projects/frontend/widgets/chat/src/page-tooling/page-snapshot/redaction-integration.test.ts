// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';

import { PageSnapshotEngine } from './engine';

afterEach(() => {
  document.body.innerHTML = '';
});

/** Capture the page and return the serialized snapshot string. */
function snapshotJson(): string {
  return JSON.stringify(new PageSnapshotEngine().capture().payload.snapshot);
}

/**
 * Integration: redaction runs inside the engine's capture pipeline, in
 * the browser, before any snapshot would leave the device. Verifies the
 * P2 success criteria — no secret/PII reaches the serialized snapshot.
 */
describe('redaction integration', () => {
  it('redacts a password field value (safe by default, no annotation)', () => {
    document.body.innerHTML = `
      <main>
        <form>
          <label for="p">Password</label>
          <input id="p" type="password" value="hunter2-secret" />
        </form>
      </main>`;
    const json = snapshotJson();
    expect(json).not.toContain('hunter2-secret');
    expect(json).toContain('‹redacted:password›');
  });

  it('redacts a secret-named field', () => {
    document.body.innerHTML = `
      <main><input name="api_key" type="text" value="raw-key-value-123" /></main>`;
    const json = snapshotJson();
    expect(json).not.toContain('raw-key-value-123');
  });

  it('redacts PII patterns inside static text', () => {
    document.body.innerHTML = `
      <main><p>Contact: jane.doe@example.com or call later</p></main>`;
    const json = snapshotJson();
    expect(json).not.toContain('jane.doe@example.com');
    expect(json).toContain('‹redacted:email›');
  });

  it('drops a data-ai-redact subtree entirely', () => {
    document.body.innerHTML = `
      <main>
        <div data-ai-redact>
          <input type="text" value="confidential-block-value" />
          <p>secret paragraph</p>
        </div>
        <p>public paragraph</p>
      </main>`;
    const json = snapshotJson();
    expect(json).not.toContain('confidential-block-value');
    expect(json).not.toContain('secret paragraph');
    expect(json).toContain('[redacted]');
    expect(json).toContain('public paragraph');
  });

  it('data-ai-include overrides a heuristic block for a safe value', () => {
    // A field named "token" would normally be redacted; data-ai-include
    // forces the (known-safe, public) value through.
    document.body.innerHTML = `
      <main>
        <input name="public_token_name" data-ai-include
               type="text" value="PUBLIC-PROJECT-ALPHA" />
      </main>`;
    const json = snapshotJson();
    expect(json).toContain('PUBLIC-PROJECT-ALPHA');
  });

  it('reports redactions in the capture telemetry', () => {
    document.body.innerHTML = `
      <main>
        <input type="password" value="p1" />
        <input name="secret_key" value="s1" />
      </main>`;
    const { telemetry } = new PageSnapshotEngine().capture();
    expect(telemetry.redactedCount).toBeGreaterThanOrEqual(2);
  });

  it('leaves a normal page completely untouched', () => {
    document.body.innerHTML = `
      <main>
        <input name="company" type="text" value="Acme Inc" />
        <p>Welcome to the dashboard</p>
      </main>`;
    const { payload, telemetry } = new PageSnapshotEngine().capture();
    const json = JSON.stringify(payload.snapshot);
    expect(json).toContain('Acme Inc');
    expect(json).toContain('Welcome to the dashboard');
    expect(telemetry.redactedCount).toBe(0);
  });
});
