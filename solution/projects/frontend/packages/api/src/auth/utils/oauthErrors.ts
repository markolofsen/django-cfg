import {
  OAuthErrorCodeEnum as OAuthErrorCodeSchema,
} from '../../_api/models';
import type { OAuthErrorCodeEnum, OAuthProviderEnum } from '../../_api/models';
import { formatAuthError } from './errors';

/** A provider the server can offer. Derived from the generated enum, so a new backend provider is a type error until it gets an adapter. */
export type OAuthProviderId = OAuthProviderEnum;

/** Every `error` value the OAuth endpoints can return (closed set from the OpenAPI schema). */
export type OAuthErrorCode = OAuthErrorCodeEnum;

/** Failures the browser detects itself, before or instead of a server answer. */
export type OAuthClientErrorCode = 'cancelled' | 'unknown_provider';

export type OAuthFailureCode = OAuthErrorCode | OAuthClientErrorCode;

export interface OAuthFailure {
  /** Set when the cause is one the UI can explain; absent for transport faults. */
  code?: OAuthFailureCode;
  /** English text for callers without a translator: server prose, else a generic sentence. */
  message: string;
}

// Read from the generated enum: a code the backend adds arrives with `make generate`.
const SERVER_CODES: ReadonlySet<string> = new Set<string>(Object.values(OAuthErrorCodeSchema.enum));

const record = (value: unknown): Record<string, unknown> | null =>
  typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : null;

/**
 * Read `{error, error_description}` off a thrown API error.
 *
 * The transport keeps the parsed body on `response`; `formatAuthError` alone
 * would surface the machine code (`invalid_state`) as if it were prose.
 */
export const readOAuthFailure = (err: unknown, fallback: string): OAuthFailure => {
  const body = record(record(err)?.response);
  const code = body?.error;
  if (typeof code === 'string' && SERVER_CODES.has(code)) {
    const description = body?.error_description;
    return {
      code: code as OAuthErrorCode,
      message: typeof description === 'string' && description ? description : fallback,
    };
  }
  return { message: formatAuthError(err, fallback) };
};
