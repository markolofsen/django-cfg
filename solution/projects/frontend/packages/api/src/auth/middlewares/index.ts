export { proxyMiddleware, proxyMiddlewareConfig } from './proxy';

// NOTE: Automatic 401 recovery and proactive refresh live in ONE place: the
// generated store (`_api/generated/helpers/auth.ts`) — interceptor, Web-Locks
// single-flight, and an auto-registered refresh handler. Do not reintroduce a
// parallel refresh path here (a former `tokenRefresh` middleware was removed
// for exactly that reason).
