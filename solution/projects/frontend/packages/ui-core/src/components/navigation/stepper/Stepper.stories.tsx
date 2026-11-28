import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Button } from '@djangocfg/ui-core/components';
import {
  Stepper,
  StepperContent,
  StepperDescription,
  StepperIndicator,
  StepperItem,
  StepperList,
  StepperNext,
  StepperPrev,
  StepperSeparator,
  StepperTitle,
  StepperTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/Stepper',
  component: Stepper,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A stepper component for multi-step workflows with keyboard navigation and validation support.',
      },
    },
  },
} satisfies Meta<typeof Stepper>;

export default meta;
type Story = StoryObj<typeof meta>;

type Step = { value: string; title: string; description: string };

// A non-empty tuple, so `steps[0]` is known to exist: having a first step is a
// real requirement of this story, not an assumption worth a `!`.
const steps: [Step, ...Step[]] = [
  { value: 'account', title: 'Account', description: 'Set up your account' },
  { value: 'profile', title: 'Profile', description: 'Personal details' },
  { value: 'settings', title: 'Settings', description: 'Configure preferences' },
  { value: 'review', title: 'Review', description: 'Review and confirm' },
];

function StepperHost(props: {
  defaultValue?: string;
  orientation?: 'horizontal' | 'vertical';
  nonInteractive?: boolean;
}) {
  const [value, setValue] = useState(props.defaultValue ?? steps[0].value);
  return (
    <Stepper
      value={value}
      onValueChange={setValue}
      orientation={props.orientation}
      nonInteractive={props.nonInteractive}
      className="w-full"
    >
      <StepperList>
        {steps.map((step) => (
          <StepperItem key={step.value} value={step.value}>
            <StepperTrigger>
              <StepperIndicator />
              <div className="flex flex-col">
                <StepperTitle>{step.title}</StepperTitle>
                <StepperDescription>{step.description}</StepperDescription>
              </div>
            </StepperTrigger>
            <StepperSeparator />
          </StepperItem>
        ))}
      </StepperList>
      {steps.map((step) => (
        <StepperContent key={step.value} value={step.value}>
          <div className="rounded-lg border p-6">
            <h3 className="font-semibold text-lg">{step.title}</h3>
            <p className="text-muted-foreground">{step.description}</p>
            <div className="mt-4 flex gap-2">
              <StepperPrev asChild>
                <Button variant="outline">Previous</Button>
              </StepperPrev>
              <StepperNext asChild>
                <Button>Next</Button>
              </StepperNext>
            </div>
          </div>
        </StepperContent>
      ))}
    </Stepper>
  );
}

export const Default: Story = {
  render: () => <StepperHost />,
};

export const Vertical: Story = {
  render: () => <StepperHost orientation="vertical" />,
};

export const NonInteractive: Story = {
  render: () => <StepperHost nonInteractive defaultValue="profile" />,
};

/**
 * Story bodies live in components, not in `render`.
 *
 * `render` is a plain callback with no identity of its own in React, so hooks
 * called there belong to whatever tree Storybook happens to mount and their
 * state survives or resets in ways nothing here controls. That is what
 * `react-hooks/rules-of-hooks` is flagging.
 */
function WithCompletedStepsDemo() {
  const [value, setValue] = useState('settings');
  return (
    <Stepper value={value} onValueChange={setValue} className="w-full">
      <StepperList>
        {steps.map((step, index) => (
          <StepperItem
            key={step.value}
            value={step.value}
            completed={index < 2}
          >
            <StepperTrigger>
              <StepperIndicator />
              <div className="flex flex-col">
                <StepperTitle>{step.title}</StepperTitle>
                <StepperDescription>{step.description}</StepperDescription>
              </div>
            </StepperTrigger>
            <StepperSeparator />
          </StepperItem>
        ))}
      </StepperList>
    </Stepper>
  );
}

export const WithCompletedSteps: Story = {
  render: () => <WithCompletedStepsDemo />,
};

function CustomIndicatorDemo() {
  const [value, setValue] = useState('account');
  return (
    <Stepper value={value} onValueChange={setValue} className="w-full">
      <StepperList>
        {steps.map((step) => (
          <StepperItem key={step.value} value={step.value}>
            <StepperTrigger>
              <StepperIndicator>
                {(state) => (
                  <span className="text-xs font-bold uppercase">
                    {state === 'completed' ? 'OK' : state === 'active' ? 'NOW' : step.value[0]}
                  </span>
                )}
              </StepperIndicator>
              <div className="flex flex-col">
                <StepperTitle>{step.title}</StepperTitle>
              </div>
            </StepperTrigger>
            <StepperSeparator />
          </StepperItem>
        ))}
      </StepperList>
    </Stepper>
  );
}

export const CustomIndicator: Story = {
  render: () => <CustomIndicatorDemo />,
};
