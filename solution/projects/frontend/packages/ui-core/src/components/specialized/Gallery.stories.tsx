import type { Meta, StoryObj } from '@storybook/react-vite';
import { ChevronRight, Folder } from 'lucide-react';
import {
  CopyButton,
  CopyField,
  Flag,
  ImageWithFallback,
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemMedia,
  ItemTitle,
  Kbd,
  KbdGroup,
  LanguageFlag,
  Portal,
  TokenIcon,
} from '@djangocfg/ui-core/components';

import { Gallery, GalleryItem, GalleryPage, GallerySection } from '../_gallery';

const meta = {
  title: 'Packages/UI Core/Specialized/Gallery',
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'The specialized odds and ends of `ui-core`, side by side. This group has no ' +
          'single theme — it is what did not fit elsewhere — so it is grouped by what ' +
          'each one is *for*: **copying a value**, **naming a thing with a glyph**, ' +
          '**composing a row**, and **escaping the DOM you are in**. ' +
          'Purely structural members (`Presence`, `Primitive`, `VisuallyHidden`) are ' +
          'omitted: they have no visual form, so a cell for them would show an empty box.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

function CopyDemo() {
  return (
    <div className="flex flex-col gap-3">
      <CopyField value="npm install @djangocfg/ui-core" />
      <div className="flex items-center gap-2">
        <CopyButton value="Copied!" variant="outline" size="sm" />
        <CopyButton value="npm install @djangocfg/ui-core" variant="ghost" size="sm">
          Copy command
        </CopyButton>
      </div>
    </div>
  );
}

function FlagDemo() {
  return (
    <div className="flex flex-wrap items-center gap-3">
      {['US', 'DE', 'JP', 'BR'].map((code) => (
        <Flag key={code} countryCode={code} rounded className="h-6 w-9" />
      ))}
      {/* LanguageFlag takes a locale, not a country — the mapping is the point. */}
      <LanguageFlag code="pt-BR" rounded className="h-6 w-9" />
    </div>
  );
}

function TokenIconDemo() {
  return (
    <div className="flex items-center gap-3">
      {['BTC', 'ETH', 'USDT', 'SOL'].map((symbol) => (
        <TokenIcon key={symbol} symbol={symbol} size={32} />
      ))}
    </div>
  );
}

function ImageWithFallbackDemo() {
  return (
    <div className="flex items-end gap-3">
      <ImageWithFallback
        src="https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=200"
        alt="Loaded"
        className="h-20 w-20 rounded-md"
      />
      <ImageWithFallback src="" alt="Fallback" fallbackIcon="image" className="h-20 w-20 rounded-md" />
      <ImageWithFallback src="" alt="Avatar" fallbackIcon="user" className="h-20 w-20 rounded-full" />
    </div>
  );
}

function KbdDemo() {
  return (
    <div className="flex flex-col gap-2 text-sm">
      <KbdGroup>
        <Kbd>⌘</Kbd>
        <Kbd>⇧</Kbd>
        <Kbd>P</Kbd>
      </KbdGroup>
      <p className="text-muted-foreground text-xs">
        Press <Kbd size="sm">⌘</Kbd> <Kbd size="sm">K</Kbd> to search.
      </p>
    </div>
  );
}

function ItemDemo() {
  return (
    <Item variant="outline">
      <ItemMedia variant="icon">
        <Folder />
      </ItemMedia>
      <ItemContent>
        <ItemTitle>Projects</ItemTitle>
        <ItemDescription>12 folders, 84 files</ItemDescription>
      </ItemContent>
      <ItemActions>
        <ChevronRight className="text-muted-foreground size-4" />
      </ItemActions>
    </Item>
  );
}

function PortalDemo() {
  return (
    <div className="flex flex-col gap-2">
      <div className="border-muted-foreground/40 rounded-md border border-dashed p-3">
        {/* disablePortal keeps the child in the cell. Without it the content
            teleports to document.body and this cell reads as broken. */}
        <Portal disablePortal>
          <span className="bg-muted rounded px-2 py-0.5 text-sm">Rendered in place</span>
        </Portal>
      </div>
      <p className="text-muted-foreground text-xs">
        Shown with <code>disablePortal</code>; by default children go to <code>document.body</code>.
      </p>
    </div>
  );
}

/**
 * The whole group on one screen.
 *
 * Grouped by purpose rather than alphabetically — this group's names share no
 * pattern, so sorting them tells the reader nothing about what to pick.
 */
export const AllSpecialized: Story = {
  render: () => (
    <GalleryPage>
      <GallerySection title="Copying a value">
        <Gallery>
          <GalleryItem name="CopyButton / CopyField" hint="Copy to clipboard, with feedback.">
            <CopyDemo />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Naming a thing with a glyph">
        <Gallery>
          <GalleryItem name="Flag" hint="Country or locale, as a flag.">
            <FlagDemo />
          </GalleryItem>
          <GalleryItem name="TokenIcon" hint="Crypto symbol, with text fallback.">
            <TokenIconDemo />
          </GalleryItem>
          <GalleryItem name="Kbd" hint="Keyboard keys and shortcut chords.">
            <KbdDemo />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Composing a row">
        <Gallery>
          <GalleryItem name="Item" hint="List row: media, content, actions.">
            <ItemDemo />
          </GalleryItem>
          <GalleryItem name="ImageWithFallback" hint="Image that survives a broken src.">
            <ImageWithFallbackDemo />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Escaping the DOM you are in">
        <Gallery>
          <GalleryItem name="Portal" hint="Render outside the local stacking context.">
            <PortalDemo />
          </GalleryItem>
        </Gallery>
      </GallerySection>
    </GalleryPage>
  ),
};
