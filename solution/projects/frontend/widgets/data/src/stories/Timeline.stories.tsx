import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Timeline,
  TimelineItem,
  TimelineContent,
  TimelineDot,
  TimelineConnector,
  TimelineHeader,
  TimelineTitle,
  TimelineDescription,
  TimelineTime,
} from '../Timeline';

const meta = {
  title: 'Widgets/Data/Timeline',
  component: Timeline,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A timeline component with vertical and horizontal orientations, alternate layout, and status support.',
      },
    },
  },
  argTypes: {
    orientation: { control: 'select', options: ['vertical', 'horizontal'] },
    variant: { control: 'select', options: ['default', 'alternate'] },
  },
} satisfies Meta<typeof Timeline>;

export default meta;
type Story = StoryObj<typeof meta>;

const events = [
  {
    id: '1',
    title: 'Project Started',
    description: 'Initial planning and kickoff meeting with the team.',
    time: 'Jan 2024',
  },
  {
    id: '2',
    title: 'Design Phase',
    description: 'Wireframes and high-fidelity mockups completed.',
    time: 'Feb 2024',
  },
  {
    id: '3',
    title: 'Development',
    description: 'Frontend and backend implementation in progress.',
    time: 'Mar 2024',
  },
  {
    id: '4',
    title: 'Testing',
    description: 'QA testing and bug fixes.',
    time: 'Apr 2024',
  },
  {
    id: '5',
    title: 'Launch',
    description: 'Production deployment and public release.',
    time: 'May 2024',
  },
];

export const Default: Story = {
  render: () => (
    <Timeline>
      {events.map((event) => (
        <TimelineItem key={event.id}>
          <TimelineDot />
          <TimelineConnector />
          <TimelineContent>
            <TimelineHeader>
              <TimelineTitle>{event.title}</TimelineTitle>
              <TimelineTime>{event.time}</TimelineTime>
            </TimelineHeader>
            <TimelineDescription>{event.description}</TimelineDescription>
          </TimelineContent>
        </TimelineItem>
      ))}
    </Timeline>
  ),
};

export const WithActiveIndex: Story = {
  render: () => (
    <Timeline activeIndex={2}>
      {events.map((event) => (
        <TimelineItem key={event.id}>
          <TimelineDot />
          <TimelineConnector />
          <TimelineContent>
            <TimelineHeader>
              <TimelineTitle>{event.title}</TimelineTitle>
              <TimelineTime>{event.time}</TimelineTime>
            </TimelineHeader>
            <TimelineDescription>{event.description}</TimelineDescription>
          </TimelineContent>
        </TimelineItem>
      ))}
    </Timeline>
  ),
};

export const Horizontal: Story = {
  render: () => (
    <Timeline orientation="horizontal">
      {events.slice(0, 4).map((event) => (
        <TimelineItem key={event.id}>
          <TimelineDot />
          <TimelineConnector />
          <TimelineContent>
            <TimelineHeader>
              <TimelineTitle>{event.title}</TimelineTitle>
              <TimelineTime>{event.time}</TimelineTime>
            </TimelineHeader>
            <TimelineDescription>{event.description}</TimelineDescription>
          </TimelineContent>
        </TimelineItem>
      ))}
    </Timeline>
  ),
};

export const Alternate: Story = {
  render: () => (
    <Timeline variant="alternate">
      {events.map((event) => (
        <TimelineItem key={event.id}>
          <TimelineDot />
          <TimelineConnector />
          <TimelineContent>
            <TimelineHeader>
              <TimelineTitle>{event.title}</TimelineTitle>
              <TimelineTime>{event.time}</TimelineTime>
            </TimelineHeader>
            <TimelineDescription>{event.description}</TimelineDescription>
          </TimelineContent>
        </TimelineItem>
      ))}
    </Timeline>
  ),
};
