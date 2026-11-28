import type { Meta, StoryObj } from '@storybook/react-vite';
import { Home } from 'lucide-react';
import {
  Breadcrumb,
  BreadcrumbEllipsis,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbNavigation,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/Breadcrumb',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink href="/">
            <Home className="mr-1 h-3.5 w-3.5" /> Home
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbLink href="/projects">Projects</BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbPage>Current Project</BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
  ),
};

export const WithEllipsis: Story = {
  render: () => (
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink href="/">Home</BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbEllipsis />
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbLink href="/projects/123">Project</BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbPage>Settings</BreadcrumbPage>
        </BreadcrumbItem>
      </BreadcrumbList>
    </Breadcrumb>
  ),
};

export const LongTrail: Story = {
  render: () => (
    <BreadcrumbNavigation
      maxItems={5}
      items={[
        { label: 'Home', href: '/', icon: <Home className="h-3.5 w-3.5" /> },
        { label: 'Workspace', href: '/workspace' },
        { label: 'Org', href: '/workspace/org' },
        { label: 'Team', href: '/workspace/org/team' },
        { label: 'Projects', href: '/workspace/org/team/projects' },
        { label: 'Engineering', href: '/workspace/org/team/projects/eng' },
        { label: 'Roadmap', href: '/workspace/org/team/projects/eng/roadmap' },
        { label: 'Q4 Plan' },
      ]}
    />
  ),
};
