import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Badge } from '@djangocfg/ui-core/components';
import {
  DataGrid,
  type DataGridColumn,
  type DataGridRowId,
} from '../DataGrid';

interface Host {
  id: number;
  hostname: string;
  region: string;
  status: 'online' | 'degraded' | 'offline';
  cpu: number;
}

const REGIONS = ['us-east', 'us-west', 'eu-central', 'ap-south'] as const;
const STATUSES = ['online', 'degraded', 'offline'] as const satisfies readonly Host['status'][];

function makeHosts(count: number): Host[] {
  return Array.from({ length: count }, (_, i) => ({
    id: i + 1,
    hostname: `host-${String(i + 1).padStart(3, '0')}.internal`,
    region: REGIONS[i % REGIONS.length] ?? REGIONS[0],
    status: STATUSES[i % STATUSES.length] ?? STATUSES[0],
    cpu: (i * 13) % 100,
  }));
}

const STATUS_VARIANT: Record<Host['status'], 'secondary' | 'outline' | 'destructive'> = {
  online: 'secondary',
  degraded: 'outline',
  offline: 'destructive',
};

const COLUMNS: DataGridColumn<Host>[] = [
  { key: 'hostname', header: 'Hostname', sortable: true, filterable: true },
  { key: 'region', header: 'Region', sortable: true, filterable: true },
  {
    key: 'status',
    header: 'Status',
    sortable: true,
    cell: (row) => <Badge variant={STATUS_VARIANT[row.status]}>{row.status}</Badge>,
  },
  {
    key: 'cpu',
    header: 'CPU %',
    align: 'right',
    sortable: true,
    cell: (row) => <span className="tabular-nums text-foreground">{row.cpu}%</span>,
  },
];

const HOSTS = makeHosts(8);

const meta = {
  title: 'Widgets/Data/DataGrid',
  component: DataGrid,
  tags: ['autodocs'],
  args: {
    data: HOSTS,
    columns: COLUMNS,
    getRowId: (row) => row.id,
  },
  render: (args) => (
    <div className="mx-auto max-w-4xl p-6">
      <DataGrid<Host> {...args} />
    </div>
  ),
} satisfies Meta<typeof DataGrid<Host>>;

export default meta;

type Story = StoryObj<typeof meta>;

/** Sortable, filterable host table with custom status + CPU cell renderers. */
export const Default: Story = {
  args: {
    initialSort: { key: 'hostname', direction: 'asc' },
  },
};

/** Larger dataset paginated client-side (DataGrid has no virtualization — pair with pagination). */
export const Paginated: Story = {
  args: {
    data: makeHosts(120),
    pageSizeOptions: [10, 25, 50],
    initialPagination: { page: 1, pageSize: 10 },
  },
};

/** Multiple selection with a live count of the selected row ids. */
export const Selection: Story = {
  args: {
    selectionMode: 'multiple',
    initialSelectedIds: [1, 3],
  },
  render: function SelectableGrid(args) {
    const [selected, setSelected] = useState<DataGridRowId[]>([1, 3]);
    return (
      <div className="mx-auto max-w-4xl space-y-3 p-6">
        <p className="text-sm text-muted-foreground">
          Selected: <span className="font-medium text-foreground">{selected.length}</span> host(s)
        </p>
        <DataGrid<Host> {...args} onSelectionChange={setSelected} />
      </div>
    );
  },
};

/** Empty state with a custom message. */
export const Empty: Story = {
  args: {
    data: [],
    emptyMessage: 'No hosts match the current filters',
  },
};
