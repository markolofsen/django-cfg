import * as React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import { Toggle } from '../data/toggle';
import { Select, SelectTrigger, SelectValue } from '../select/select';
import { Button } from './button';
import { CONTROL_SIZE, type FieldControlSize } from './control-size';
import { DateField } from './datetime-field';
import { Tabs, TabsList, TabsTrigger } from '../navigation/tabs';
import { Input } from './input';
import { Textarea } from './textarea';
import { InputGroup } from './input-group';

const FIELD_SIZES: FieldControlSize[] = ['xs', 'sm', 'default', 'lg'];

/** Class tokens of the first element's `class` attribute in `html`. */
function classTokens(html: string): string[] {
  const match = /class="([^"]*)"/.exec(html);
  expect(match, `no class attribute in: ${html}`).not.toBeNull();
  return (match?.[1] ?? "").split(/\s+/).filter(Boolean);
}

/** Height utilities (`h-*`, not `min-h-*`) a control carries. */
const heightTokens = (tokens: string[]) => tokens.filter((token) => /^h-/.test(token));

/** The fixed-height token of a rung (its `h-*` class), without the touch floor. */
const rung = (size: keyof typeof CONTROL_SIZE) => heightTokens(CONTROL_SIZE[size].height.split(' '));

const render = (element: React.ReactElement) => classTokens(renderToStaticMarkup(element));

describe('control height ladder', () => {
  it('is the documented ladder', () => {
    expect(
      Object.fromEntries(Object.entries(CONTROL_SIZE).map(([name, spec]) => [name, spec.height])),
    ).toEqual({
      xs: 'h-(--control-h-xs) pointer-coarse:min-h-11',
      sm: 'h-(--control-h-sm) pointer-coarse:min-h-11',
      default: 'h-(--control-h-default) pointer-coarse:min-h-11',
      lg: 'h-(--control-h-lg) pointer-coarse:min-h-11',
      huge: 'h-(--control-h-huge)',
    });
  });

  it.each(FIELD_SIZES)('Button, Input and Select trigger share the %s height', (size) => {
    const expected = rung(size);

    const button = render(<Button size={size}>Go</Button>);
    const input = render(<Input inputSize={size} />);
    const trigger = render(
      <Select>
        <SelectTrigger size={size}>
          <SelectValue />
        </SelectTrigger>
      </Select>,
    );

    expect(heightTokens(button)).toEqual(expected);
    expect(heightTokens(input)).toEqual(expected);
    expect(heightTokens(trigger)).toEqual(expected);
  });

  it.each(FIELD_SIZES)('the grouped and date fields share the %s height', (size) => {
    const expected = rung(size);

    expect(heightTokens(render(<InputGroup inputSize={size} />))).toEqual(expected);
    expect(heightTokens(render(<DateField inputSize={size} />))).toEqual(expected);
  });

  it('keeps Button-only sizes on the ladder', () => {
    expect(heightTokens(render(<Button size="huge">Go</Button>))).toEqual(rung('huge'));
    expect(heightTokens(render(<Button size="icon">Go</Button>))).toEqual(rung('default'));
  });

  it('keeps Toggle on the ladder where it has a matching size', () => {
    for (const size of ['sm', 'default', 'lg'] as const) {
      expect(heightTokens(render(<Toggle size={size}>T</Toggle>))).toEqual(rung(size));
    }
  });

  it('applies the size on an uncontrolled Input too', () => {
    expect(heightTokens(render(<Input inputSize="lg" defaultValue="x" />))).toEqual(rung('lg'));
  });

  it('defaults every control to the same size', () => {
    const defaults = [
      render(<Button>Go</Button>),
      render(<Input />),
      render(
        <Select>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
        </Select>,
      ),
    ].map(heightTokens);

    expect(defaults).toEqual([rung('default'), rung('default'), rung('default')]);
  });

  it.each(FIELD_SIZES)('floors the %s rung at 44px on a coarse pointer, never below the mouse height', (size) => {
    expect(CONTROL_SIZE[size].height).toContain('pointer-coarse:min-h-11');
    expect(CONTROL_SIZE[size].minHeight).toContain('pointer-coarse:min-h-11');
    expect(render(<Button size={size}>Go</Button>)).toContain('pointer-coarse:min-h-11');
    expect(render(<Input inputSize={size} />)).toContain('pointer-coarse:min-h-11');
  });

  it('makes the icon button 44px wide as well as tall on a coarse pointer', () => {
    expect(render(<Button size="icon">Go</Button>)).toEqual(
      expect.arrayContaining(['pointer-coarse:min-h-11', 'pointer-coarse:min-w-11']),
    );
  });

  it('types the text fields 16px on a phone and 14px from md', () => {
    const trigger = render(
      <Select>
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
      </Select>,
    );
    for (const tokens of [render(<Input />), render(<Textarea />), render(<Textarea bare />), trigger]) {
      expect(tokens).toEqual(expect.arrayContaining(['text-base', 'md:text-sm']));
      expect(tokens).not.toContain('text-sm');
    }
  });

  it('gives a tab trigger a 44px touch height and its track room for it', () => {
    const html = renderToStaticMarkup(
      <Tabs defaultValue="a">
        <TabsList variant="pill">
          <TabsTrigger value="a">A</TabsTrigger>
        </TabsList>
      </Tabs>,
    );
    const classes = [...html.matchAll(/class="([^"]*)"/g)].map((m) => m[1] ?? '');
    const list = classes.find((c) => c.includes('tabs-sliding')) ?? '';
    const trigger = classes.find((c) => c.includes('rounded-full') && !c.includes('tabs-sliding')) ?? '';
    expect(trigger).toContain('pointer-coarse:min-h-11');
    expect(list).toContain('pointer-coarse:h-12');
  });
});
