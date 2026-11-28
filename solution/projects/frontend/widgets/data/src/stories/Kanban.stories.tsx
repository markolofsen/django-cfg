import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Badge } from '@djangocfg/ui-core/components';
import {
  Kanban,
  type KanbanColumnType,
  type KanbanCardId,
  type KanbanColumnId,
} from '../Kanban';

const BOARD: KanbanColumnType[] = [
  {
    id: 'backlog',
    title: 'Backlog',
    cards: [
      { id: 't-1', title: 'Audit auth flow', description: 'Map every redirect after login.' },
      { id: 't-2', title: 'Spike: edge caching', description: 'Compare Vercel vs Cloudflare.' },
      { id: 't-3', title: 'Triage flaky tests' },
    ],
  },
  {
    id: 'in-progress',
    title: 'In progress',
    cards: [
      { id: 't-4', title: 'Migrate billing webhooks', description: 'Stripe → internal queue.' },
      { id: 't-5', title: 'DataGrid keyboard nav' },
    ],
  },
  {
    id: 'done',
    title: 'Done',
    cards: [
      { id: 't-6', title: 'Ship dark mode tokens', description: 'Semantic palette landed.' },
      { id: 't-7', title: 'Storybook 8 upgrade' },
    ],
  },
];

const meta = {
  title: 'Widgets/Data/Kanban',
  component: Kanban,
  tags: ['autodocs'],
  args: { columns: BOARD },
  render: (args) => (
    <div className="mx-auto max-w-5xl p-6">
      <Kanban {...args} />
    </div>
  ),
} satisfies Meta<typeof Kanban>;

export default meta;

type Story = StoryObj<typeof meta>;

/** Three-column task board. Drag a card across columns to reorder/move. */
export const Default: Story = {};

/** Controlled board: `onMoveCard` / `onReorderCard` mutate local state so moves persist. */
export const Controlled: Story = {
  render: function ControlledKanban(args) {
    const [columns, setColumns] = useState<KanbanColumnType[]>(args.columns);

    const moveCard = (
      cardId: KanbanCardId,
      fromColumnId: KanbanColumnId,
      toColumnId: KanbanColumnId,
      toIndex: number,
    ) => {
      setColumns((cols) => {
        const card = cols
          .find((c) => c.id === fromColumnId)
          ?.cards.find((cd) => cd.id === cardId);
        if (!card) return cols;
        return cols.map((col) => {
          if (col.id === fromColumnId) {
            return { ...col, cards: col.cards.filter((cd) => cd.id !== cardId) };
          }
          if (col.id === toColumnId) {
            const next = [...col.cards];
            next.splice(toIndex, 0, card);
            return { ...col, cards: next };
          }
          return col;
        });
      });
    };

    const reorderCard = (columnId: KanbanColumnId, cardId: KanbanCardId, toIndex: number) => {
      setColumns((cols) =>
        cols.map((col) => {
          if (col.id !== columnId) return col;
          const from = col.cards.findIndex((cd) => cd.id === cardId);
          if (from === -1) return col;
          const next = [...col.cards];
          const [card] = next.splice(from, 1);
          if (!card) return col;
          next.splice(toIndex, 0, card);
          return { ...col, cards: next };
        }),
      );
    };

    return (
      <div className="mx-auto max-w-5xl p-6">
        <Kanban {...args} columns={columns} onMoveCard={moveCard} onReorderCard={reorderCard} />
      </div>
    );
  },
};

/** Custom card + column-header renderers using `meta` and semantic tokens. */
const TEMPLATED_BOARD: KanbanColumnType[] = BOARD.map((col) => ({
  ...col,
  cards: col.cards.map((card, i) => ({
    ...card,
    meta: { priority: i === 0 ? 'high' : 'normal', points: (i + 1) * 2 },
  })),
}));

export const CustomTemplates: Story = {
  args: {
    columns: TEMPLATED_BOARD,
    renderColumnHeader: (column) => (
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-foreground">{column.title}</span>
        <Badge variant="secondary">{column.cards.length}</Badge>
      </div>
    ),
    renderCard: (card) => {
      const priority = (card.meta?.priority as string) ?? 'normal';
      const points = (card.meta?.points as number) ?? 0;
      return (
        <div className="space-y-2">
          <div className="flex items-center justify-between gap-2">
            <h4 className="text-sm font-medium text-foreground">{card.title}</h4>
            <Badge variant={priority === 'high' ? 'destructive' : 'outline'}>{priority}</Badge>
          </div>
          {card.description && <p className="text-xs text-muted-foreground">{card.description}</p>}
          <p className="text-xs text-muted-foreground">{points} pts</p>
        </div>
      );
    },
  },
};

/** Loading state and an empty column message. */
export const States: Story = {
  args: {
    columns: [
      { id: 'todo', title: 'To do', cards: [{ id: 'a', title: 'Write the RFC' }] },
      { id: 'empty', title: 'Review', cards: [] },
    ],
    emptyColumnMessage: 'Nothing to review yet',
  },
  render: (args) => (
    <div className="mx-auto max-w-5xl space-y-6 p-6">
      <Kanban {...args} />
      <div className="h-[200px]">
        <Kanban columns={BOARD} loading />
      </div>
    </div>
  ),
};
