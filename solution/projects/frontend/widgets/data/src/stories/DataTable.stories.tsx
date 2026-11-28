'use client';

import type { Meta, StoryObj } from '@storybook/react-vite';
import { Badge } from '@djangocfg/ui-core/components';
import { DataTable, type DataTableColumn } from '../DataTable';

interface TeamMember {
  id: number;
  email: string;
  role: string;
}

const TEAM: TeamMember[] = [
  { id: 1, email: 'owner@example.com', role: 'owner' },
];

const TEAM_COLUMNS: DataTableColumn<TeamMember>[] = [
  { key: 'email', header: 'Email', sortable: true },
  {
    key: 'role',
    header: 'Role',
    sortable: true,
    cell: (row) => <Badge variant="secondary">{row.role}</Badge>,
  },
  { key: 'actions', header: 'Actions', align: 'right', cell: () => null },
];

const meta = {
  title: 'Widgets/Data/DataTable',
  component: DataTable,
  tags: ['autodocs'],
  args: {
    data: TEAM,
    columns: TEAM_COLUMNS,
    getRowId: (row) => row.id,
  },
  render: (args) => (
    <div className="mx-auto max-w-4xl p-6">
      <DataTable<TeamMember> {...args} />
    </div>
  ),
} satisfies Meta<typeof DataTable<TeamMember>>;

export default meta;

type Story = StoryObj<typeof meta>;

/** Reproduces the "Team" panel from the cmdop Account page: few rows + footer pagination. */
export const TeamPanel: Story = {
  args: {
    pageSizeOptions: [25, 50, 100],
    initialPagination: { page: 1, pageSize: 25 },
  },
};

const USERS: TeamMember[] = Array.from({ length: 7 }, (_, i) => ({
  id: i + 1,
  email: `user${i + 1}@example.com`,
  role: i === 0 ? 'owner' : 'member',
}));

export const ManyRows: Story = {
  args: {
    data: USERS,
    selectionMode: 'multiple',
    pageSizeOptions: [5, 10, 25],
    initialPagination: { page: 1, pageSize: 5 },
  },
};
