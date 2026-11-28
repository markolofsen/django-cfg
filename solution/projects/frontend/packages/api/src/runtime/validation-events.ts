import type { ZodError } from 'zod';
import { diagnosticReference, diagnosticUrl, printDiagnostic } from './request-diagnostics';

export interface ValidationErrorDetail {
  /** Stable operation label; the mutator uses `METHOD path`. */
  operation: string;
  path: string;
  method: string;
  error: ZodError;
  response: unknown;
  timestamp: Date;
  /** One support reference shared by the browser console and error UI. */
  reference?: string;
  /** Bounded schema-only diagnostic, without response values or error messages. */
  diagnostic?: string;
}

export type ValidationErrorEvent = CustomEvent<ValidationErrorDetail>;

const EVENT_NAME = 'zod-validation-error';

function validationDiagnostic(error: ZodError): string {
  const issues = error.issues;
  const lines = issues.slice(0, 20).map(issue => {
    // A record key can contain an email, a token, or another response value.
    // Print field-shaped keys only. Do not print custom issue.message or input.
    const path = issue.path.map((part, index) =>
      typeof part === 'number' ? `[${part}]` :
        typeof part === 'string' && /^[a-zA-Z_][a-zA-Z0-9_-]{0,63}$/.test(part)
          ? (index ? '.' : '') + part : '[key]'
    ).join('') || 'root';
    const metadata = issue as unknown as Record<string, unknown>;
    const constraints = ['expected', 'format', 'pattern', 'minimum', 'maximum']
      .flatMap(key => {
        const value = metadata[key];
        return typeof value === 'number' || typeof value === 'bigint' ||
          (typeof value === 'string' && value.length <= 200)
          ? [`${key}=${String(value)}`] : [];
      }).join(', ');
    return `${path}: ${issue.code}${constraints ? ` (${constraints})` : ''}`;
  });
  if (issues.length > 20) lines.push(`... ${issues.length - 20} more issues`);
  return `Response schema validation failed (${issues.length} issues)\n${lines.join('\n')}`;
}

/** Dispatch a browser diagnostic without ever turning observability into a request failure. */
export function dispatchValidationError(detail: ValidationErrorDetail): void {
  if (typeof window === 'undefined' || typeof CustomEvent === 'undefined') return;
  const reference = detail.reference ?? diagnosticReference();
  let diagnostic = 'Response schema validation failed';
  try {
    diagnostic = validationDiagnostic(detail.error);
    // Use the console even on public production sites, regardless of debug
    // mode or whether an app has mounted the optional error UI.
    // The existing devtools event subscriber captures the same diagnostic.
    printDiagnostic('validation', reference, detail.method, detail.path, diagnostic);
  } catch {
    // A console extension or broken formatter must not interrupt a request.
  }
  try {
    window.dispatchEvent(new CustomEvent<ValidationErrorDetail>(EVENT_NAME, {
      detail: { ...detail, reference, diagnostic, path: diagnosticUrl(detail.path), operation: `${detail.method} ${diagnosticUrl(detail.path)}` },
      bubbles: true,
      cancelable: false,
    }));
  } catch {
    // Diagnostics must never alter the generated operation's error contract.
  }
}

/** Subscribe to response/schema validation diagnostics in browser applications. */
export function onValidationError(
  callback: (detail: ValidationErrorDetail) => void,
): () => void {
  if (typeof window === 'undefined') return () => {};
  const handler = (event: Event) => {
    if (event instanceof CustomEvent) callback((event as ValidationErrorEvent).detail);
  };
  window.addEventListener(EVENT_NAME, handler);
  return () => window.removeEventListener(EVENT_NAME, handler);
}

