import * as React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { RouterAdapterProvider, defaultAdapter, type RouterAdapter } from './adapter';
import { parseAsInteger, parseAsString } from './parsers';
import { useQueryState, type UseQueryStateOptions } from './useQueryState';

/** A window whose History API really moves `location`, so live reads see earlier writes. */
function stubWindow(href: string) {
  const loc = { href: '', pathname: '', search: '', hash: '' };
  const set = (u: string) => {
    const url = new URL(u, 'http://site.test');
    Object.assign(loc, { href: url.href, pathname: url.pathname, search: url.search, hash: url.hash });
  };
  set(href);
  const history = {
    pushState: vi.fn((_s: unknown, _t: string, u: string) => set(u)),
    replaceState: vi.fn((_s: unknown, _t: string, u: string) => set(u)),
  };
  vi.stubGlobal('window', { location: loc, history });
  return { loc, history };
}

type Setter = (n: unknown, o?: UseQueryStateOptions) => void;

function mount(adapter: RouterAdapter, hookOpts?: UseQueryStateOptions) {
  const out: { tab?: Setter; page?: Setter } = {};
  function Probe() {
    out.tab = useQueryState('tab', parseAsString, hookOpts)[1] as Setter;
    out.page = useQueryState('page', parseAsInteger.withDefault(1), hookOpts)[1] as Setter;
    return null;
  }
  renderToStaticMarkup(
    <RouterAdapterProvider value={adapter}>
      <Probe />
    </RouterAdapterProvider>,
  );
  return out as Required<typeof out>;
}

function spyAdapter(): RouterAdapter & { push: ReturnType<typeof vi.fn>; replace: ReturnType<typeof vi.fn>; shallow: ReturnType<typeof vi.fn> } {
  return {
    ...defaultAdapter,
    push: vi.fn(),
    replace: vi.fn(),
    shallow: vi.fn(),
  } as never;
}

beforeEach(() => stubWindow('http://site.test/view?x=1'));
afterEach(() => vi.unstubAllGlobals());

describe('useQueryState shallow', () => {
  it('writes through shallow and never calls push or replace', () => {
    const a = spyAdapter();
    mount(a, { shallow: true }).tab('side');
    expect(a.shallow).toHaveBeenCalledWith('/view?x=1&tab=side', { replace: false });
    expect(a.push).not.toHaveBeenCalled();
    expect(a.replace).not.toHaveBeenCalled();
  });

  it('is off by default: the normal navigation runs', () => {
    const a = spyAdapter();
    mount(a).tab('side');
    expect(a.shallow).not.toHaveBeenCalled();
    expect(a.push).toHaveBeenCalledWith('/view?x=1&tab=side', { scroll: false, progress: false });
  });

  it('the call overrides the hook, both ways', () => {
    const a = spyAdapter();
    mount(a, { shallow: true }).tab('a', { shallow: false });
    expect(a.push).toHaveBeenCalledTimes(1);
    expect(a.shallow).not.toHaveBeenCalled();
    mount(a).tab('b', { shallow: true });
    expect(a.shallow).toHaveBeenCalledTimes(1);
  });

  it('replace goes to the adapter, state is null in the default adapter', () => {
    const { history } = stubWindow('http://site.test/view');
    mount(defaultAdapter, { shallow: true, replace: true }).tab('side');
    expect(history.replaceState).toHaveBeenCalledWith(null, '', '/view?tab=side');
    expect(history.pushState).not.toHaveBeenCalled();
    mount(defaultAdapter, { shallow: true }).tab('top');
    expect(history.pushState).toHaveBeenCalledWith(null, '', '/view?tab=top');
  });

  it('two calls in one tick keep both parameters', () => {
    const { loc } = stubWindow('http://site.test/view');
    const s = mount(defaultAdapter, { shallow: true, replace: true });
    s.tab('side');
    s.page(3);
    expect(loc.search).toBe('?tab=side&page=3');
  });

  it('a functional updater sees the write made a moment earlier', () => {
    const { loc } = stubWindow('http://site.test/view');
    const s = mount(defaultAdapter, { shallow: true, replace: true });
    s.page(2);
    s.page((p: number) => p + 1);
    expect(loc.search).toBe('?page=3');
  });

  it('null clears the key and the default value drops it', () => {
    const { loc } = stubWindow('http://site.test/view?tab=a&page=4');
    const s = mount(defaultAdapter, { shallow: true, replace: true });
    s.tab(null);
    expect(loc.search).toBe('?page=4');
    s.page(1);
    expect(loc.search).toBe('');
  });

  it('keeps the hash on a shallow write', () => {
    const { loc } = stubWindow('http://site.test/view#top');
    mount(defaultAdapter, { shallow: true, replace: true }).tab('x');
    expect(loc.hash).toBe('#top');
    expect(loc.search).toBe('?tab=x');
  });

  it('an adapter without shallow falls back to push/replace with bar and scroll off', () => {
    const a = { ...defaultAdapter, push: vi.fn(), replace: vi.fn(), shallow: undefined } as unknown as RouterAdapter;
    mount(a, { shallow: true, replace: true }).tab('x');
    expect(a.replace).toHaveBeenCalledWith('/view?x=1&tab=x', { scroll: false, progress: false });
  });
});
