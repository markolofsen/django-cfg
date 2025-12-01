import type { Metadata } from 'next';
import { ContactView } from './ContactView';
import { generateMetadata } from '@core/metadata';

export const metadata: Metadata = generateMetadata({
  title: 'Contact Us',
  description: 'Get in touch with the DjangoCFG team',
});

export default function ContactPage() {
  return <ContactView />;
}
