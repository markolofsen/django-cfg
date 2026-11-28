'use client';

import { useEffect, useState } from 'react';

import type { McpServer, McpServerInfo } from '../install';
import { fetchServerInfo } from './serverInfo';

/** The server's `/info/` summary once there is a key to ask with; null before that, and when the server does not answer. */
export function useServerInfo(server: McpServer, key: string | null): McpServerInfo | null {
  const [info, setInfo] = useState<McpServerInfo | null>(null);
  useEffect(() => {
    if (!key) return;
    const abort = new AbortController();
    void fetchServerInfo(server, key, abort.signal).then((next) => {
      if (!abort.signal.aborted) setInfo(next);
    });
    return () => abort.abort();
  }, [server.url, key]); // eslint-disable-line react-hooks/exhaustive-deps -- by value: the url, not the object
  return key ? info : null;
}
