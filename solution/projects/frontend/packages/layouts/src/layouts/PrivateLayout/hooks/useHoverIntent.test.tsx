// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { useHoverIntent, type HoverIntent, type HoverIntentOptions } from './useHoverIntent';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let host: HTMLElement;
let root: Root;
let intent: HoverIntent;

function Probe(props: HoverIntentOptions) {
  intent = useHoverIntent(props);
  return null;
}

function mount(props: HoverIntentOptions = { openDelay: 400, closeDelay: 250 }) {
  act(() => root.render(<Probe {...props} />));
}

const mouse = { pointerType: 'mouse' };

beforeEach(() => {
  vi.useFakeTimers();
  host = document.createElement('div');
  root = createRoot(host);
});

afterEach(() => {
  act(() => root.unmount());
  vi.useRealTimers();
});

describe('useHoverIntent', () => {
  it('opens only after the open delay', () => {
    mount();
    act(() => intent.zoneProps.onPointerEnter(mouse));
    act(() => void vi.advanceTimersByTime(399));
    expect(intent.open).toBe(false);
    act(() => void vi.advanceTimersByTime(1));
    expect(intent.open).toBe(true);
  });

  it('a pass-by shorter than the open delay never opens', () => {
    mount();
    act(() => intent.zoneProps.onPointerEnter(mouse));
    act(() => void vi.advanceTimersByTime(200));
    act(() => intent.zoneProps.onPointerLeave(mouse));
    act(() => void vi.advanceTimersByTime(1000));
    expect(intent.open).toBe(false);
  });

  it('closes after the grace delay, and returning in time keeps it open', () => {
    mount();
    act(() => intent.zoneProps.onPointerEnter(mouse));
    act(() => void vi.advanceTimersByTime(400));
    expect(intent.open).toBe(true);

    act(() => intent.panelProps.onPointerLeave(mouse));
    act(() => void vi.advanceTimersByTime(200));
    act(() => intent.panelProps.onPointerEnter(mouse));
    act(() => void vi.advanceTimersByTime(1000));
    expect(intent.open).toBe(true);

    act(() => intent.panelProps.onPointerLeave(mouse));
    act(() => void vi.advanceTimersByTime(249));
    expect(intent.open).toBe(true);
    act(() => void vi.advanceTimersByTime(1));
    expect(intent.open).toBe(false);
  });

  it('ignores touch pointers', () => {
    mount();
    act(() => intent.zoneProps.onPointerEnter({ pointerType: 'touch' }));
    act(() => void vi.advanceTimersByTime(1000));
    expect(intent.open).toBe(false);
  });

  it('never opens when disabled', () => {
    mount({ enabled: false });
    act(() => intent.zoneProps.onPointerEnter(mouse));
    act(() => void vi.advanceTimersByTime(1000));
    expect(intent.open).toBe(false);
  });

  it('stays open while pinned and closes after the grace once released', () => {
    mount();
    act(() => intent.zoneProps.onPointerEnter(mouse));
    act(() => void vi.advanceTimersByTime(400));
    act(() => intent.pin(true));
    act(() => intent.panelProps.onPointerLeave(mouse));
    act(() => void vi.advanceTimersByTime(2000));
    expect(intent.open).toBe(true);
    act(() => intent.pin(false));
    act(() => void vi.advanceTimersByTime(250));
    expect(intent.open).toBe(false);
  });
});
