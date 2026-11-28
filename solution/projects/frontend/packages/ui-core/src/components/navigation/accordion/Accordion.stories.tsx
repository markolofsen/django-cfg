import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/Accordion',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

const items = [
  {
    q: 'What is djangocfg?',
    a: 'A monorepo of TypeScript packages that pair with the Django CFG backend.',
  },
  {
    q: 'Does it work outside Next.js?',
    a: '`ui-core` is Next.js-free; the Next router adapter ships as `@djangocfg/ui-core/adapters/nextjs`, and Next server utilities live in `@djangocfg/nextjs`.',
  },
  {
    q: 'Where do I report issues?',
    a: 'github.com/markolofsen/django-cfg — issues are triaged weekly.',
  },
];

export const Single: Story = {
  render: () => (
    <Accordion type="single" collapsible className="w-[480px]">
      {items.map((it, i) => (
        <AccordionItem key={i} value={`q-${i}`}>
          <AccordionTrigger>{it.q}</AccordionTrigger>
          <AccordionContent>{it.a}</AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  ),
};

export const Multiple: Story = {
  render: () => (
    <Accordion type="multiple" className="w-[480px]">
      {items.map((it, i) => (
        <AccordionItem key={i} value={`q-${i}`}>
          <AccordionTrigger>{it.q}</AccordionTrigger>
          <AccordionContent>{it.a}</AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  ),
};

const FAQ_ITEMS = [
  {
    q: 'What payment methods do you accept?',
    a: 'Visa, MasterCard, AMEX, PayPal, and bank transfers — all processed securely.',
  },
  {
    q: 'How long does shipping take?',
    a: 'Standard: 5-7 business days. Express: 2-3 days. International varies.',
  },
  {
    q: 'What is your return policy?',
    a: '30-day return policy for unused items in original packaging.',
  },
];

export const FAQ: Story = {
  render: () => (
    <Accordion type="single" collapsible className="w-[560px]">
      {FAQ_ITEMS.map((it, i) => (
        <AccordionItem key={i} value={`faq-${i}`}>
          <AccordionTrigger>{it.q}</AccordionTrigger>
          <AccordionContent>{it.a}</AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  ),
};

export const WithDefaultOpen: Story = {
  render: () => (
    <Accordion type="single" defaultValue="q-1" className="w-[480px]">
      {items.map((it, i) => (
        <AccordionItem key={i} value={`q-${i}`}>
          <AccordionTrigger>{it.q}</AccordionTrigger>
          <AccordionContent>{it.a}</AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  ),
};
