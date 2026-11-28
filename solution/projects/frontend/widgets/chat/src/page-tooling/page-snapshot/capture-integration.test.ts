// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';

import { PageSnapshotEngine } from './engine';

afterEach(() => {
  document.body.innerHTML = '';
});

/**
 * Integration: capture realistic pages end-to-end through the engine
 * (scope → walk → fold → budget). Verifies the P1 success criteria —
 * a 100-row data table, with folding, stays within budget.
 */
describe('capture integration', () => {
  it('captures a settings form sensibly and well under budget', () => {
    document.body.innerHTML = `
      <nav>global nav</nav>
      <main>
        <h1>Billing Settings</h1>
        <form>
          <label for="company">Company</label>
          <input id="company" type="text" value="Acme Inc" />
          <label for="plan">Plan</label>
          <select id="plan"><option selected>Pro</option></select>
          <button type="submit">Save</button>
        </form>
      </main>`;

    const { payload, telemetry } = new PageSnapshotEngine().capture();
    const json = JSON.stringify(payload.snapshot);

    // Content is present, chrome is not.
    expect(json).toContain('Billing Settings');
    expect(json).toContain('Company');
    expect(json).not.toContain('global nav');

    // Comfortably small.
    expect(payload.metadata.tokenEstimate).toBeLessThan(500);
    expect(telemetry.degradation).toBe('none');
    expect(telemetry.scopeTier).toBe('tier2-main');
  });

  it('captures a 100-row table within budget thanks to folding', () => {
    const rows = Array.from(
      { length: 100 },
      (_, i) => `
        <tr>
          <td>Client ${i}</td>
          <td>client${i}@example.com</td>
          <td><button>Edit</button></td>
        </tr>`,
    ).join('');
    document.body.innerHTML = `
      <main>
        <table><tbody>${rows}</tbody></table>
      </main>`;

    const { payload, telemetry } = new PageSnapshotEngine().capture();

    // Folding fired — the 100 identical rows collapsed.
    expect(telemetry.foldedCount).toBeGreaterThan(0);

    // The whole snapshot stays within the default 8k budget.
    expect(payload.metadata.tokenEstimate).toBeLessThan(8_000);

    // The collapse marker is present.
    expect(JSON.stringify(payload.snapshot)).toContain('collapsed');
  });

  it('a 100-row table WITHOUT folding would be far larger (sanity)', () => {
    // Same table; confirm the folded result is dramatically smaller
    // than the raw row count would imply (~100 rows × 3 cells).
    const rows = Array.from(
      { length: 100 },
      (_, i) => `<tr><td>Client ${i}</td><td>x${i}</td></tr>`,
    ).join('');
    document.body.innerHTML = `<main><table><tbody>${rows}</tbody></table></main>`;

    const { payload } = new PageSnapshotEngine().capture();
    const interactiveAndText = JSON.stringify(payload.snapshot).length;
    // Folded snapshot is small — nowhere near 100 rows of serialized CST.
    expect(interactiveAndText).toBeLessThan(4_000);
  });
});
