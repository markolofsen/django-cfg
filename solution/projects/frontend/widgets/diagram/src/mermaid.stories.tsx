import type { Meta, StoryObj } from '@storybook/react-vite';
import * as React from 'react';
import { LazyMermaid as Mermaid } from '.';

// ============================================================================
// Curated diagram payloads
// ============================================================================

const FLOWCHART = `graph TD
  A[Client] -->|HTTP| B(Next.js)
  B --> C{Auth?}
  C -->|yes| D[Render]
  C -->|no| E[/Redirect/]`;

const SEQUENCE = `sequenceDiagram
  participant U as User
  participant W as WebApp
  participant API as Backend
  U->>W: click "Save"
  W->>API: PATCH /profile
  API-->>W: 200 OK
  W-->>U: toast "Saved"`;

const GANTT = `gantt
  title djangocfg storybook rollout
  dateFormat YYYY-MM-DD
  section Phases
  Scaffold        :done, p1, 2026-05-18, 1d
  Workspaces      :done, p2, after p1, 1d
  UI seed         :done, p3, after p2, 2d
  Demo migration  :active, p4, after p3, 3d
  Ship            :p5, after p4, 2d`;

const CLASS_DIAGRAM = `classDiagram
  class Animal {
    +String name
    +int age
    +makeSound() void
  }
  class Dog {
    +String breed
    +bark() void
  }
  class Cat {
    +bool indoor
    +meow() void
  }
  Animal <|-- Dog
  Animal <|-- Cat`;

const STATE_DIAGRAM = `stateDiagram-v2
  [*] --> Idle
  Idle --> Loading: fetch()
  Loading --> Success: 200 OK
  Loading --> Error: 5xx
  Success --> Idle: reset
  Error --> Idle: retry
  Success --> [*]`;

const ER_DIAGRAM = `erDiagram
  CUSTOMER ||--o{ ORDER : places
  ORDER ||--|{ LINE_ITEM : contains
  CUSTOMER {
    string name
    string email
  }
  ORDER {
    int id
    date created
  }
  LINE_ITEM {
    string sku
    int qty
    float price
  }`;

const MINDMAP = `mindmap
  root((djangocfg))
    Frontend
      Next.js
      Storybook
      UI Tools
    Backend
      Django
      DRF
      Celery
    Infra
      Docker
      Postgres
      Redis`;

const PIE = `pie title Browser usage
  "Chrome" : 62
  "Safari" : 18
  "Firefox" : 9
  "Edge" : 7
  "Other" : 4`;

const TIMELINE = `timeline
  title djangocfg release timeline
  2024 : Project kickoff : Core packages
  2025 : Public beta : UI Tools v1
  2026 : Storybook reorg : Mermaid stories`;

const JOURNEY = `journey
  title User onboarding
  section Discovery
    Visit landing: 5: User
    Read features: 4: User
  section Sign up
    Click signup: 5: User
    Fill form: 2: User
    Verify email: 4: User, System
  section First run
    Complete profile: 3: User
    Create project: 5: User`;

// ============================================================================
// Meta
// ============================================================================

const Frame: React.FC<React.PropsWithChildren> = ({ children }) => (
  <div className="w-[720px] rounded-lg border border-border bg-card p-4">
    {children}
  </div>
);

const meta = {
  title: 'Widgets/Diagram/Mermaid',
  component: Mermaid,
  tags: ['autodocs'],
  argTypes: {
    chart: { control: 'text', table: { category: 'Content' } },
    fullscreen: {
      control: 'boolean',
      description: 'Enable click-to-fullscreen overlay',
      table: { category: 'Behaviour', defaultValue: { summary: 'true' } },
    },
    isCompact: {
      control: 'boolean',
      description: 'Use compact layout',
      table: { category: 'Behaviour', defaultValue: { summary: 'false' } },
    },
    scrollIsolation: {
      control: 'boolean',
      description: 'Enable the FloatingToolbar scroll-lock overlay',
      table: { category: 'Behaviour', defaultValue: { summary: 'false' } },
    },
    className: { control: 'text', table: { category: 'Styling' } },
  },
  render: (args) => (
    <Frame>
      <Mermaid {...args} />
    </Frame>
  ),
} satisfies Meta<typeof Mermaid>;

export default meta;

type Story = StoryObj<typeof meta>;

// ============================================================================
// Playground (Controls-driven)
// ============================================================================

export const Playground: Story = {
  args: {
    chart: FLOWCHART,
    fullscreen: true,
    isCompact: false,
    scrollIsolation: false,
  },
};

// ============================================================================
// Curated presets
// ============================================================================

export const Flowchart: Story = {
  args: { chart: FLOWCHART },
};

export const Sequence: Story = {
  args: { chart: SEQUENCE },
};

export const Gantt: Story = {
  args: { chart: GANTT },
};

export const Class: Story = {
  args: { chart: CLASS_DIAGRAM },
};

export const State: Story = {
  args: { chart: STATE_DIAGRAM },
};

export const ER: Story = {
  args: { chart: ER_DIAGRAM },
};

export const Mindmap: Story = {
  args: { chart: MINDMAP },
};

export const Pie: Story = {
  args: { chart: PIE },
};

export const Timeline: Story = {
  args: { chart: TIMELINE },
};

export const Journey: Story = {
  args: { chart: JOURNEY },
};
