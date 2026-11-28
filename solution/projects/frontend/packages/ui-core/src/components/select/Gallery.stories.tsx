import { useMemo, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Combobox,
  ComboboxAsync,
  CountrySelect,
  LanguageSelect,
  MultiSelect,
  MultiSelectPro,
  MultiSelectProAsync,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@djangocfg/ui-core/components';

import { Gallery, GalleryItem, GalleryPage, GallerySection } from '../_gallery';

const meta = {
  title: 'Packages/UI Core/Select/Gallery',
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'Every select in `ui-core`, side by side. Eight components overlap heavily — ' +
          'this page exists to answer *which one*, which is the question a per-component ' +
          'story cannot answer. Pick along two axes: **one value or many**, and ' +
          '**who owns the option list** (you, or a server).',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

const FRUIT = [
  { value: 'apple', label: 'Apple' },
  { value: 'banana', label: 'Banana' },
  { value: 'cherry', label: 'Cherry' },
  { value: 'durian', label: 'Durian', disabled: true },
];

/** Stands in for a server: filters a fixed list after a tick. */
function useFakeSearch(query: string) {
  const options = useMemo(
    () => FRUIT.filter((o) => o.label.toLowerCase().includes(query.toLowerCase())),
    [query],
  );
  return options;
}

function SingleSelect() {
  const [value, setValue] = useState('apple');
  return (
    <Select value={value} onValueChange={setValue}>
      <SelectTrigger>
        <SelectValue placeholder="Pick a fruit" />
      </SelectTrigger>
      <SelectContent>
        {FRUIT.map((o) => (
          <SelectItem key={o.value} value={o.value} disabled={o.disabled}>
            {o.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

function SingleCombobox() {
  const [value, setValue] = useState('banana');
  return <Combobox options={FRUIT} value={value} onValueChange={setValue} />;
}

function AsyncCombobox() {
  const [value, setValue] = useState<string | null>('cherry');
  const [search, setSearch] = useState('');
  const options = useFakeSearch(search);
  return (
    <ComboboxAsync
      options={options}
      value={value}
      onValueChange={setValue}
      searchValue={search}
      onSearchChange={setSearch}
      clearable
    />
  );
}

function Multi() {
  const [value, setValue] = useState<string[]>(['apple', 'cherry']);
  return <MultiSelect options={FRUIT} value={value} onChange={setValue} />;
}

function MultiPro() {
  const [value, setValue] = useState<string[]>(['apple']);
  return (
    <MultiSelectPro options={FRUIT} defaultValue={value} onValueChange={setValue} maxCount={2} />
  );
}

function MultiProAsync() {
  const [search, setSearch] = useState('');
  const options = useFakeSearch(search);
  return (
    <MultiSelectProAsync
      options={options}
      defaultValue={['banana']}
      searchValue={search}
      onSearchChange={setSearch}
    />
  );
}

function Countries() {
  const [value, setValue] = useState<string[]>(['US']);
  return <CountrySelect value={value} onChange={setValue} />;
}

function Languages() {
  const [value, setValue] = useState<string[]>(['en']);
  return <LanguageSelect value={value} onChange={setValue} />;
}

/**
 * The whole group on one screen.
 *
 * Grouped by the decision you are actually making — how many values, and who
 * owns the list — rather than alphabetically, which sorts `Combobox` next to
 * `CountrySelect` and tells you nothing.
 */
export const AllSelects: Story = {
  render: () => (
    <GalleryPage>
      <GallerySection title="Single value">
        <Gallery>
          <GalleryItem name="Select" hint="Short, known list. No search.">
            <SingleSelect />
          </GalleryItem>
          <GalleryItem name="Combobox" hint="Same, plus type-to-filter.">
            <SingleCombobox />
          </GalleryItem>
          <GalleryItem name="ComboboxAsync" hint="List comes from a server; you own the query.">
            <AsyncCombobox />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Many values">
        <Gallery>
          <GalleryItem name="MultiSelect" hint="Plain multi-select with a search box.">
            <Multi />
          </GalleryItem>
          <GalleryItem name="MultiSelectPro" hint="Badges, icons, grouping, overflow count.">
            <MultiPro />
          </GalleryItem>
          <GalleryItem name="MultiSelectProAsync" hint="MultiSelectPro over a server-fed list.">
            <MultiProAsync />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Pre-filled domains">
        <Gallery>
          <GalleryItem name="CountrySelect" hint="ISO country list and flags, built in.">
            <Countries />
          </GalleryItem>
          <GalleryItem name="LanguageSelect" hint="Language list with native names.">
            <Languages />
          </GalleryItem>
        </Gallery>
      </GallerySection>
    </GalleryPage>
  ),
};

/**
 * The same eight, disabled.
 *
 * A disabled control is the state most likely to be wrong and least likely to
 * be checked — it is off the happy path in every individual story.
 */
export const DisabledStates: Story = {
  render: () => (
    <GalleryPage>
      <Gallery>
        <GalleryItem name="Select">
          <Select disabled>
            <SelectTrigger>
              <SelectValue placeholder="Disabled" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="a">A</SelectItem>
            </SelectContent>
          </Select>
        </GalleryItem>
        <GalleryItem name="Combobox">
          <Combobox options={FRUIT} disabled placeholder="Disabled" />
        </GalleryItem>
        <GalleryItem name="ComboboxAsync">
          <ComboboxAsync
            options={[]}
            value={null}
            onValueChange={() => {}}
            searchValue=""
            onSearchChange={() => {}}
            disabled
            placeholder="Disabled"
          />
        </GalleryItem>
        <GalleryItem name="MultiSelect">
          <MultiSelect options={FRUIT} disabled placeholder="Disabled" />
        </GalleryItem>
        <GalleryItem name="MultiSelectPro">
          <MultiSelectPro options={FRUIT} disabled placeholder="Disabled" />
        </GalleryItem>
        <GalleryItem name="MultiSelectProAsync">
          <MultiSelectProAsync
            options={[]}
            searchValue=""
            onSearchChange={() => {}}
            disabled
            placeholder="Disabled"
          />
        </GalleryItem>
        <GalleryItem name="CountrySelect">
          <CountrySelect disabled placeholder="Disabled" />
        </GalleryItem>
        <GalleryItem name="LanguageSelect">
          <LanguageSelect disabled placeholder="Disabled" />
        </GalleryItem>
      </Gallery>
    </GalleryPage>
  ),
};
