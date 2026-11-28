import type { MDXComponents } from 'nextra/mdx-components';
import { useMDXComponents as getDocsMDXComponents } from 'nextra-theme-docs';
import { Callout, Tabs } from 'nextra/components';

import { TLDR } from '@components/ui/mdx/TLDR';
import { FaqJsonLd } from '@components/seo/json-ld';
import { DocCard, DocCards } from '@components/mdx/DocCards';
import { Contacts } from '@components/mdx/Contacts';

const docsComponents = getDocsMDXComponents();

// Vercel-style cards: title-first, description below. Allow <Cards.Card> too.
const Cards = Object.assign(DocCards, { Card: DocCard });

export function useMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...docsComponents,
    Tabs,
    Callout,
    Cards,
    Card: DocCard,
    CardGrid: DocCards,
    TLDR,
    Contacts,
    FaqJsonLd,
    ...components,
  };
}
