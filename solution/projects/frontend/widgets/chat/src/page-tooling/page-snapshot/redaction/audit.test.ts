import { describe, expect, it } from 'vitest';

import { RedactionAuditor } from './audit';

describe('RedactionAuditor', () => {
  it('counts scanned elements and redactions', () => {
    const auditor = new RedactionAuditor();
    auditor.markScanned();
    auditor.markScanned();
    auditor.log({ elementRole: 'input', triggerReason: 'heuristic' });

    const report = auditor.report();
    expect(report.totalElementsScanned).toBe(2);
    expect(report.totalRedactedCount).toBe(1);
    expect(report.entries[0]?.triggerReason).toBe('heuristic');
    expect(auditor.redactedCount).toBe(1);
  });

  it('starts empty', () => {
    const report = new RedactionAuditor().report();
    expect(report.totalElementsScanned).toBe(0);
    expect(report.totalRedactedCount).toBe(0);
    expect(report.entries).toEqual([]);
  });
});
