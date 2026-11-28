/** The stream ended because nothing arrived for the idle limit, or the connection broke mid-stream. The stored message is the truth: reconcile. */
export class StreamLostError extends Error {
  readonly reason: 'idle' | 'network';

  constructor(reason: 'idle' | 'network') {
    super(`stream lost (${reason})`);
    this.reason = reason;
  }
}

/** One block (lines up to a blank line) to its JSON payload: `:` comment lines are skipped, `data:` lines are joined, malformed JSON is dropped. */
function payloadOf(block: string): unknown {
  const data: string[] = [];
  for (const line of block.split('\n')) {
    if (line.startsWith(':')) continue;
    if (line.startsWith('data:')) data.push(line.slice(line.charAt(5) === ' ' ? 6 : 5));
  }
  if (data.length === 0) return undefined;
  try {
    return JSON.parse(data.join('\n'));
  } catch {
    return undefined;
  }
}

const withIdle = <T,>(read: Promise<T>, idleMs: number): Promise<T> =>
  new Promise<T>((resolve, reject) => {
    const timer = setTimeout(() => reject(new StreamLostError('idle')), idleMs);
    read.then(
      (value) => {
        clearTimeout(timer);
        resolve(value);
      },
      (error: unknown) => {
        clearTimeout(timer);
        reject(error);
      },
    );
  });

/**
 * JSON payloads of a Server-Sent Events body, in order. Blocks end at a blank line (`\n\n`, `\r\n\r\n`); a trailing partial block is flushed at the end;
 * a multi-byte character split across chunks is decoded whole. Throws `StreamLostError` on the idle limit or a read failure; an abort by the caller ends quietly.
 */
export async function* parseSSE(body: ReadableStream<Uint8Array>, options: { idleMs: number; signal?: AbortSignal }): AsyncGenerator<unknown> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  try {
    for (;;) {
      let chunk: ReadableStreamReadResult<Uint8Array>;
      try {
        chunk = await withIdle(reader.read(), options.idleMs);
      } catch (error) {
        if (options.signal?.aborted) return;
        throw error instanceof StreamLostError ? error : new StreamLostError('network');
      }
      if (chunk.done) break;
      buffer += decoder.decode(chunk.value, { stream: true }).replace(/\r\n?/g, '\n');
      let cut = buffer.indexOf('\n\n');
      while (cut !== -1) {
        const payload = payloadOf(buffer.slice(0, cut));
        buffer = buffer.slice(cut + 2);
        if (payload !== undefined) yield payload;
        cut = buffer.indexOf('\n\n');
      }
    }
    buffer += decoder.decode().replace(/\r\n?/g, '\n');
    if (buffer.trim()) {
      const payload = payloadOf(buffer);
      if (payload !== undefined) yield payload;
    }
  } finally {
    reader.cancel().catch(() => undefined);
  }
}
