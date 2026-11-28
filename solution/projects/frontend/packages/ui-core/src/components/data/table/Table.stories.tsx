import { useMemo, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { ArrowDown, ArrowUp, ArrowUpDown } from 'lucide-react';
import {
  Badge,
  Checkbox,
  Skeleton,
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/Table',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

const ROWS = [
  { id: 'INV001', method: 'Credit Card', status: 'Paid', amount: '$250.00' },
  { id: 'INV002', method: 'PayPal', status: 'Pending', amount: '$150.00' },
  { id: 'INV003', method: 'Bank Transfer', status: 'Unpaid', amount: '$350.00' },
  { id: 'INV004', method: 'Credit Card', status: 'Paid', amount: '$450.00' },
];

const USERS = [
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'Active' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User', status: 'Active' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User', status: 'Inactive' },
];

const statusVariant: Record<string, 'default' | 'secondary' | 'destructive'> = {
  Paid: 'default',
  Pending: 'secondary',
  Unpaid: 'destructive',
};

export const Default: Story = {
  render: () => (
    <div className="w-[640px]">
      <Table>
        <TableCaption>A list of recent invoices.</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">Invoice</TableHead>
            <TableHead>Method</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Amount</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {ROWS.map((r) => (
            <TableRow key={r.id}>
              <TableCell className="font-medium">{r.id}</TableCell>
              <TableCell>{r.method}</TableCell>
              <TableCell>
                <Badge variant={statusVariant[r.status]}>{r.status}</Badge>
              </TableCell>
              <TableCell className="text-right">{r.amount}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  ),
};

export const WithBadges: Story = {
  render: () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Role</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {USERS.map((u) => (
          <TableRow key={u.id}>
            <TableCell className="font-medium">{u.name}</TableCell>
            <TableCell>{u.email}</TableCell>
            <TableCell>
              <Badge variant="secondary">{u.role}</Badge>
            </TableCell>
            <TableCell>
              <Badge variant={u.status === 'Active' ? 'default' : 'outline'}>
                {u.status}
              </Badge>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  ),
};

export const Striped: Story = {
  render: () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Invoice</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Method</TableHead>
          <TableHead className="text-right">Amount</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody striped>
        {ROWS.map((r) => (
          <TableRow key={r.id}>
            <TableCell className="font-medium">{r.id}</TableCell>
            <TableCell>{r.status}</TableCell>
            <TableCell>{r.method}</TableCell>
            <TableCell className="text-right">{r.amount}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  ),
};

export const Compact: Story = {
  render: () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="h-8">Invoice</TableHead>
          <TableHead className="h-8">Status</TableHead>
          <TableHead className="h-8">Amount</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {ROWS.slice(0, 3).map((r) => (
          <TableRow key={r.id}>
            <TableCell className="py-2">{r.id}</TableCell>
            <TableCell className="py-2">{r.status}</TableCell>
            <TableCell className="py-2">{r.amount}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  ),
};

type SortKey = 'id' | 'method' | 'status' | 'amount';
type SortDir = 'asc' | 'desc';

function SortableTable() {
  const [sortKey, setSortKey] = useState<SortKey>('id');
  const [sortDir, setSortDir] = useState<SortDir>('asc');

  const toggle = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const sorted = useMemo(() => {
    const parseAmount = (s: string) => Number(s.replace(/[^0-9.]/g, ''));
    const arr = [...ROWS];
    arr.sort((a, b) => {
      const av = sortKey === 'amount' ? parseAmount(a.amount) : a[sortKey];
      const bv = sortKey === 'amount' ? parseAmount(b.amount) : b[sortKey];
      if (av < bv) return sortDir === 'asc' ? -1 : 1;
      if (av > bv) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
    return arr;
  }, [sortKey, sortDir]);

  const SortIcon = ({ k }: { k: SortKey }) => {
    if (sortKey !== k) return <ArrowUpDown className="ml-1 inline h-3 w-3 opacity-50" />;
    return sortDir === 'asc'
      ? <ArrowUp className="ml-1 inline h-3 w-3" />
      : <ArrowDown className="ml-1 inline h-3 w-3" />;
  };

  return (
    <div className="w-[640px]">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead onClick={() => toggle('id')} className="cursor-pointer select-none">
              Invoice<SortIcon k="id" />
            </TableHead>
            <TableHead onClick={() => toggle('method')} className="cursor-pointer select-none">
              Method<SortIcon k="method" />
            </TableHead>
            <TableHead onClick={() => toggle('status')} className="cursor-pointer select-none">
              Status<SortIcon k="status" />
            </TableHead>
            <TableHead
              onClick={() => toggle('amount')}
              className="cursor-pointer select-none text-right"
            >
              Amount<SortIcon k="amount" />
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((r) => (
            <TableRow key={r.id}>
              <TableCell className="font-medium">{r.id}</TableCell>
              <TableCell>{r.method}</TableCell>
              <TableCell>
                <Badge variant={statusVariant[r.status]}>{r.status}</Badge>
              </TableCell>
              <TableCell className="text-right">{r.amount}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

function SelectableTable() {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const allSelected = selected.size === ROWS.length;
  const someSelected = selected.size > 0 && !allSelected;

  const toggleAll = (checked: boolean) => {
    setSelected(checked ? new Set(ROWS.map((r) => r.id)) : new Set());
  };
  const toggleRow = (id: string, checked: boolean) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (checked) next.add(id);
      else next.delete(id);
      return next;
    });
  };

  return (
    <div className="w-[640px] space-y-2">
      <div className="text-sm text-muted-foreground">
        {selected.size} of {ROWS.length} row(s) selected.
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[40px]">
              <Checkbox
                checked={allSelected ? true : someSelected ? 'indeterminate' : false}
                onCheckedChange={(v) => toggleAll(Boolean(v))}
                aria-label="Select all"
              />
            </TableHead>
            <TableHead>Invoice</TableHead>
            <TableHead>Method</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Amount</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {ROWS.map((r) => {
            const isSelected = selected.has(r.id);
            return (
              <TableRow key={r.id} data-state={isSelected ? 'selected' : undefined}>
                <TableCell>
                  <Checkbox
                    checked={isSelected}
                    onCheckedChange={(v) => toggleRow(r.id, Boolean(v))}
                    aria-label={`Select ${r.id}`}
                  />
                </TableCell>
                <TableCell className="font-medium">{r.id}</TableCell>
                <TableCell>{r.method}</TableCell>
                <TableCell>
                  <Badge variant={statusVariant[r.status]}>{r.status}</Badge>
                </TableCell>
                <TableCell className="text-right">{r.amount}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}

export const Sortable: Story = { render: () => <SortableTable /> };
export const Selectable: Story = { render: () => <SelectableTable /> };

export const WithFooter: Story = {
  render: () => {
    const total = ROWS.reduce(
      (sum, r) => sum + Number(r.amount.replace(/[^0-9.]/g, '')),
      0
    );
    return (
      <div className="w-[640px]">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[100px]">Invoice</TableHead>
              <TableHead>Method</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Amount</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {ROWS.map((r) => (
              <TableRow key={r.id}>
                <TableCell className="font-medium">{r.id}</TableCell>
                <TableCell>{r.method}</TableCell>
                <TableCell>
                  <Badge variant={statusVariant[r.status]}>{r.status}</Badge>
                </TableCell>
                <TableCell className="text-right">{r.amount}</TableCell>
              </TableRow>
            ))}
          </TableBody>
          <TableFooter>
            <TableRow>
              <TableCell colSpan={3}>Total</TableCell>
              <TableCell className="text-right">${total.toFixed(2)}</TableCell>
            </TableRow>
          </TableFooter>
        </Table>
      </div>
    );
  },
};

const METHODS = ['Credit Card', 'PayPal', 'Bank Transfer'] as const;
const STATUSES = ['Paid', 'Pending', 'Unpaid'] as const;

/** `% 3` over a 3-tuple always lands in range; `at(...)!` would assert that, a
 *  modulo-indexed lookup with a fallback states it. */
const cycle = <T,>(values: readonly [T, ...T[]], i: number): T =>
  values[i % values.length] ?? values[0];

const MANY_ROWS = Array.from({ length: 30 }, (_, i) => ({
  id: `INV${String(i + 1).padStart(3, '0')}`,
  method: cycle(METHODS, i),
  status: cycle(STATUSES, i),
  amount: `$${((i + 1) * 50).toFixed(2)}`,
}));

export const StickyHeader: Story = {
  render: () => (
    <div className="w-[640px]">
      <Table containerClassName="max-h-[320px]">
        <TableHeader sticky>
          <TableRow>
            <TableHead className="w-[100px]">Invoice</TableHead>
            <TableHead>Method</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Amount</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {MANY_ROWS.map((r) => (
            <TableRow key={r.id}>
              <TableCell className="font-medium">{r.id}</TableCell>
              <TableCell>{r.method}</TableCell>
              <TableCell>
                <Badge variant={statusVariant[r.status]}>{r.status}</Badge>
              </TableCell>
              <TableCell className="text-right">{r.amount}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  ),
};

export const Loading: Story = {
  render: () => (
    <div className="w-[640px]">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">Invoice</TableHead>
            <TableHead>Method</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Amount</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.from({ length: 5 }).map((_, i) => (
            <TableRow key={i}>
              <TableCell>
                <Skeleton className="h-4 w-16" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-4 w-24" />
              </TableCell>
              <TableCell>
                <Skeleton className="h-5 w-16 rounded-full" />
              </TableCell>
              <TableCell className="text-right">
                <Skeleton className="ml-auto h-4 w-20" />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  ),
};

export const Empty: Story = {
  render: () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Invoice</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Amount</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell colSpan={3} className="h-24 text-center text-muted-foreground">
            No results.
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  ),
};
