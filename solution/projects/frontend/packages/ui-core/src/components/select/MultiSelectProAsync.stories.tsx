import { useEffect, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Building2, Globe, Mail, MapPin, Phone, User } from 'lucide-react';
import {
  Label,
  MultiSelectProAsync,
  type MultiSelectProAsyncOption,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/MultiSelectProAsync',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Async multi-select. The parent owns `options`, `searchValue`, `isLoading`; the component is purely controlled.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

const DATASET: MultiSelectProAsyncOption[] = [
  { value: 'acme', label: 'ACME Corp', icon: Building2, description: 'Manufacturing' },
  { value: 'globex', label: 'Globex', icon: Globe, description: 'Tech' },
  { value: 'initech', label: 'Initech', icon: Mail, description: 'Software' },
  { value: 'umbrella', label: 'Umbrella', icon: MapPin, description: 'Biotech' },
  { value: 'soylent', label: 'Soylent', icon: User, description: 'Food' },
  { value: 'wayland', label: 'Wayland-Yutani', icon: Phone, description: 'Defense' },
  { value: 'stark', label: 'Stark Industries', icon: Building2, description: 'Energy' },
  { value: 'wonka', label: 'Wonka Industries', icon: Globe, description: 'Confectionery' },
];

function simulateFetch(
  query: string,
  delayMs = 300,
): Promise<MultiSelectProAsyncOption[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const q = query.trim().toLowerCase();
      if (!q) {
        resolve(DATASET.slice(0, 5));
        return;
      }
      resolve(
        DATASET.filter(
          (item) =>
            item.label.toLowerCase().includes(q) ||
            item.description?.toLowerCase().includes(q),
        ),
      );
    }, delayMs);
  });
}

function DefaultHost() {
  const [value, setValue] = useState<string[]>([]);
  const [search, setSearch] = useState('');
  const [options, setOptions] = useState<MultiSelectProAsyncOption[]>([]);
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
    <div className="grid w-96 gap-1.5">
      <Label>Companies</Label>
      <MultiSelectProAsync
        options={options}
        defaultValue={value}
        onValueChange={setValue}
        searchValue={search}
        onSearchChange={setSearch}
        isLoading={loading}
        placeholder="Search companies…"
        searchPlaceholder="Type to search…"
        loadingText="Searching…"
        maxCount={3}
      />
      <p className="text-xs text-muted-foreground">Selected: {value.join(', ') || '(none)'}</p>
    </div>
  );
}

export const Default: Story = {
  render: () => <DefaultHost />,
};
