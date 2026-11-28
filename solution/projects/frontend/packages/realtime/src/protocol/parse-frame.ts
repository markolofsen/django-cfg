import type { ErrorFrame, MsgFrame, ServerFrame, SubErrorCode, SubOkFrame } from './frames';

export type ParseResult =
  | { ok: true; frame: ServerFrame }
  | { ok: false; reason: string };

const SUB_ERROR_CODES: ReadonlySet<string> = new Set<SubErrorCode>([
  'forbidden',
  'unknown_topic',
  'invalid',
  'limit',
  'timeout',
]);

type Fields = Record<string, unknown>;

function isFields(value: unknown): value is Fields {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

const str = (v: unknown): v is string => typeof v === 'string';
const int = (v: unknown): v is number => typeof v === 'number' && Number.isInteger(v);

function isSubErrorCode(v: unknown): v is SubErrorCode {
  return str(v) && SUB_ERROR_CODES.has(v);
}

function fail(reason: string): ParseResult {
  return { ok: false, reason };
}

/**
 * The only place an incoming frame is narrowed. Unknown fields are dropped,
 * an unknown `op` or a missing field is refused, and nothing here throws.
 */
export function parseFrame(text: string): ParseResult {
  let raw: unknown;
  try {
    raw = JSON.parse(text);
  } catch {
    return fail('not JSON');
  }
  if (!isFields(raw)) return fail('not an object');
  const f = raw;

  switch (f.op) {
    case 'hello': {
      const user = f.user;
      const userOk = user === null || str(user) || typeof user === 'number';
      if (!int(f.v) || !userOk || typeof f.ping !== 'number' || !str(f.cid)) {
        return fail('hello: bad fields');
      }
      return { ok: true, frame: { op: 'hello', v: f.v, user, ping: f.ping, cid: f.cid } };
    }
    case 'sub_ok': {
      if (!int(f.id) || !str(f.topic) || !(f.offset === null || str(f.offset))) {
        return fail('sub_ok: bad fields');
      }
      if (f.recovered !== undefined && typeof f.recovered !== 'boolean') {
        return fail('sub_ok: bad recovered');
      }
      const frame: SubOkFrame = { op: 'sub_ok', id: f.id, topic: f.topic, offset: f.offset };
      if (typeof f.recovered === 'boolean') frame.recovered = f.recovered;
      return { ok: true, frame };
    }
    case 'sub_err': {
      if (!int(f.id) || !str(f.topic) || !isSubErrorCode(f.code)) {
        return fail('sub_err: bad fields');
      }
      return { ok: true, frame: { op: 'sub_err', id: f.id, topic: f.topic, code: f.code } };
    }
    case 'msg': {
      if (!str(f.topic) || !str(f.offset) || !('data' in f)) return fail('msg: bad fields');
      if (f.origin_cid !== undefined && !str(f.origin_cid)) return fail('msg: bad origin_cid');
      const frame: MsgFrame = { op: 'msg', topic: f.topic, offset: f.offset, data: f.data };
      if (str(f.origin_cid)) frame.origin_cid = f.origin_cid;
      return { ok: true, frame };
    }
    case 'error': {
      if (!str(f.code)) return fail('error: bad code');
      const frame: ErrorFrame = { op: 'error', code: f.code };
      if (str(f.detail)) frame.detail = f.detail;
      return { ok: true, frame };
    }
    case 'pong':
      return { ok: true, frame: { op: 'pong' } };
    default:
      return fail(`unknown op ${JSON.stringify(f.op)}`);
  }
}
