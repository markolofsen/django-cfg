import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, within } from 'storybook/test';
import {
  Button,
  CONTROL_SIZE,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  type FieldControlSize,
} from '@djangocfg/ui-core/components';

/**
 * Pixel height each size name must resolve to. The guide lines are drawn from
 * these numbers, not from the components, so a control that drifts off the
 * ladder visibly leaves the lines.
 */
const GUIDE_PX: Record<FieldControlSize, number> = { xs: 28, sm: 32, default: 36, lg: 44 };
const SIZES = Object.keys(CONTROL_SIZE).filter((name) => name !== 'huge') as FieldControlSize[];

function AlignmentRow({ size }: { size: FieldControlSize }) {
  const px = GUIDE_PX[size];
  return (
    <div className="grid gap-1.5">
      <div className="font-mono text-xs text-muted-foreground">
        {size} · {px}px · {CONTROL_SIZE[size].height}
      </div>
      <div
        data-testid={`row-${size}`}
        className="relative flex items-start gap-3 outline-dashed outline-1 outline-fuchsia-500/60"
      >
        <span
          aria-hidden
          className="pointer-events-none absolute inset-x-0 z-10 border-t border-dashed border-fuchsia-500"
          style={{ top: px }}
        />
        <Input inputSize={size} placeholder="Input" className="w-40" />
        <Select defaultValue="a">
          <SelectTrigger size={size} className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="a">Select</SelectItem>
            <SelectItem value="b">Other</SelectItem>
          </SelectContent>
        </Select>
        <Input inputSize={size} type="date" className="w-40" />
        <Button size={size} variant="outline">
          Button
        </Button>
      </div>
    </div>
  );
}

const meta = {
  title: 'Packages/UI Core/Controls/Alignment',
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'One row per size: `Input`, `SelectTrigger`, a date `Input` and a `Button`, top-aligned ' +
          'inside a dashed outline. All four read their height from `CONTROL_SIZE` ' +
          '(`forms/control-size.ts`), so every control touches both guide lines at every size. ' +
          'A control that falls off the ladder shows as a ragged top or bottom edge.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj<typeof meta>;

export const Ladder: Story = {
  render: () => (
    <div className="grid gap-6">
      {SIZES.map((size) => (
        <AlignmentRow key={size} size={size} />
      ))}
    </div>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    for (const size of SIZES) {
      const row = canvas.getByTestId(`row-${size}`);
      const controls = row.querySelectorAll<HTMLElement>('input, button[role="combobox"], button:not([role])');
      expect(controls.length).toBe(4);
      for (const control of controls) {
        expect(Math.round(control.getBoundingClientRect().height)).toBe(GUIDE_PX[size]);
      }
    }
  },
};
