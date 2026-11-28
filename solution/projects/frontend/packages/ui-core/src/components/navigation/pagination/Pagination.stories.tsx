import { useMemo, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { StaticPagination } from '@djangocfg/ui-core/components';
import type { DRFPaginatedResponse } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/Pagination',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

function buildResponse(page: number, totalItems: number, pageSize: number): DRFPaginatedResponse<{ id: number }> {
  const pages = Math.max(1, Math.ceil(totalItems / pageSize));
  const safePage = Math.min(Math.max(1, page), pages);
  return {
    count: totalItems,
    page: safePage,
    pages,
    page_size: pageSize,
    has_next: safePage < pages,
    has_previous: safePage > 1,
    next_page: safePage < pages ? safePage + 1 : null,
    previous_page: safePage > 1 ? safePage - 1 : null,
    results: Array.from({ length: Math.min(pageSize, totalItems - (safePage - 1) * pageSize) }, (_, i) => ({
      id: (safePage - 1) * pageSize + i + 1,
    })),
  };
}

function PaginationDemo({ totalItems, pageSize = 10 }: { totalItems: number; pageSize?: number }) {
  const [page, setPage] = useState(1);
  const data = useMemo(() => buildResponse(page, totalItems, pageSize), [page, totalItems, pageSize]);
  return (
    <div className="space-y-4">
      <div className="text-sm text-muted-foreground">
        Current page: <span className="font-mono">{data.page}</span> / {data.pages}
      </div>
      <StaticPagination data={data} onPageChange={setPage} />
    </div>
  );
}

export const Default: Story = {
  render: () => <PaginationDemo totalItems={100} pageSize={10} />,
};

export const SmallTotal: Story = {
  render: () => <PaginationDemo totalItems={25} pageSize={10} />,
};

export const LargeTotal: Story = {
  render: () => <PaginationDemo totalItems={5_000} pageSize={20} />,
};

export const WithPageSize: Story = {
  render: () => <PaginationDemo totalItems={500} pageSize={50} />,
};
