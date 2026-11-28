import { useEffect, useMemo, useRef, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { ComboboxAsync, Label, type ComboboxAsyncOption } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/ComboboxAsync',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Single-select combobox with parent-owned async search. The parent feeds `options`, `searchValue` and `isLoading`; the component is purely controlled.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

const ALL_USERS: ComboboxAsyncOption[] = [
  { value: 'u-1', label: 'Alice Anderson', description: 'alice@example.com' },
  { value: 'u-2', label: 'Bob Brown', description: 'bob@example.com' },
  { value: 'u-3', label: 'Charlie Chen', description: 'charlie@example.com' },
  { value: 'u-4', label: 'Diana Davis', description: 'diana@example.com' },
  { value: 'u-5', label: 'Ethan Edwards', description: 'ethan@example.com' },
  { value: 'u-6', label: 'Fiona Foster', description: 'fiona@example.com' },
  { value: 'u-7', label: 'George Grant', description: 'george@example.com' },
  { value: 'u-8', label: 'Hannah Hayes', description: 'hannah@example.com' },
];

function simulateFetch(query: string, delayMs = 300): Promise<ComboboxAsyncOption[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const q = query.trim().toLowerCase();
      if (!q) {
        resolve(ALL_USERS.slice(0, 5));
        return;
      }
      resolve(
        ALL_USERS.filter(
          (u) =>
            u.label.toLowerCase().includes(q) ||
            u.description?.toLowerCase().includes(q),
        ),
      );
    }, delayMs);
  });
}

function DefaultHost() {
  const [value, setValue] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [options, setOptions] = useState<ComboboxAsyncOption[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    simulateFetch(search).then((res) => {
      if (cancelled) return;
      setOptions(res);
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [search]);

  return (
    <div className="grid w-80 gap-1.5">
      <Label>User</Label>
      <ComboboxAsync
        options={options}
        value={value}
        onValueChange={setValue}
        searchValue={search}
        onSearchChange={setSearch}
        isLoading={loading}
        placeholder="Search users…"
        searchPlaceholder="Type a name or email…"
      />
      <p className="text-xs text-muted-foreground">Selected: {value ?? '(none)'}</p>
    </div>
  );
}

export const Default: Story = {
  render: () => <DefaultHost />,
};

function useDebouncedValue<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

function WithDebounceHost() {
  const [value, setValue] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const debouncedSearch = useDebouncedValue(search, 400);
  const [options, setOptions] = useState<ComboboxAsyncOption[]>([]);
  const [loading, setLoading] = useState(false);
  const fetchCountRef = useRef(0);
  const [fetchCount, setFetchCount] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    simulateFetch(debouncedSearch).then((res) => {
      if (cancelled) return;
      fetchCountRef.current += 1;
      setFetchCount(fetchCountRef.current);
      setOptions(res);
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [debouncedSearch]);

  return (
    <div className="grid w-80 gap-1.5">
      <Label>User (debounced 400ms)</Label>
      <ComboboxAsync
        options={options}
        value={value}
        onValueChange={setValue}
        searchValue={search}
        onSearchChange={setSearch}
        isLoading={loading}
        placeholder="Search users…"
      />
      <p className="text-xs text-muted-foreground">Fetches issued: {fetchCount}</p>
    </div>
  );
}

export const WithDebounce: Story = {
  render: () => <WithDebounceHost />,
};

function WithErrorHandlingHost() {
  const [value, setValue] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [options, setOptions] = useState<ComboboxAsyncOption[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    new Promise<ComboboxAsyncOption[]>((resolve, reject) => {
      setTimeout(() => {
        if (search.toLowerCase().includes('fail')) {
          reject(new Error('Simulated network failure'));
        } else {
          resolve(ALL_USERS.filter((u) =>
            u.label.toLowerCase().includes(search.toLowerCase()),
          ).slice(0, 5));
        }
      }, 300);
    })
      .then((res) => {
        if (cancelled) return;
        setOptions(res);
        setLoading(false);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setOptions([]);
        setLoading(false);
        setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [search]);

  const emptyText = useMemo(
    () => (error ? `Error: ${error}` : 'No matches'),
    [error],
  );

  return (
    <div className="grid w-80 gap-1.5">
      <Label>User (try typing &quot;fail&quot;)</Label>
      <ComboboxAsync
        options={options}
        value={value}
        onValueChange={setValue}
        searchValue={search}
        onSearchChange={setSearch}
        isLoading={loading}
        placeholder="Search users…"
        emptyText={emptyText}
      />
      {error && (
        <p className="text-xs text-destructive">Last error: {error}</p>
      )}
    </div>
  );
}

export const WithErrorHandling: Story = {
  render: () => <WithErrorHandlingHost />,
};
