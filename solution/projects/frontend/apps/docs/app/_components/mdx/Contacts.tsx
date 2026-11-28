import { Mail, MessageSquare, CalendarDays, MapPin } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

import { settings } from '@core/settings';

/**
 * Contact channel cards for the /contact MDX page.
 *
 * All values come from `settings.contact` (single source of truth). Icons are
 * lucide-react. MDX uses a bare `<Contacts />` — no props, no hardcoded URLs.
 */

const { email, whatsapp, calendly, location } = settings.contact;

/** wa.me wants digits only (no '+', spaces or dashes). */
const whatsappDigits = whatsapp.replace(/[^\d]/g, '');

type Channel = {
  icon: LucideIcon;
  label: string;
  value: string;
  href: string;
  cta: string;
  external?: boolean;
};

/** Primary, action-oriented contact channels. */
const channels: Channel[] = [
  {
    icon: Mail,
    label: 'Email',
    value: email,
    href: `mailto:${email}`,
    cta: 'Write to us',
  },
  {
    icon: CalendarDays,
    label: 'Book a call',
    value: 'Talk to the team',
    href: calendly,
    cta: 'Schedule a meeting',
    external: true,
  },
  {
    icon: MessageSquare,
    label: 'WhatsApp',
    value: whatsapp,
    href: `https://wa.me/${whatsappDigits}`,
    cta: 'Start a chat',
    external: true,
  },
];

export function Contacts() {
  return (
    <div className="contacts">
      {channels.map(({ icon: Icon, label, value, href, cta, external }) => (
        <a
          key={label}
          className="contacts__card"
          href={href}
          {...(external ? { target: '_blank', rel: 'noreferrer' } : {})}
        >
          <span className="contacts__icon" aria-hidden="true">
            <Icon size={20} strokeWidth={2} />
          </span>
          <span className="contacts__body">
            <span className="contacts__label">{label}</span>
            <span className="contacts__value">{value}</span>
            <span className="contacts__cta">
              {cta}
              <span className="contacts__arrow" aria-hidden="true">
                →
              </span>
            </span>
          </span>
        </a>
      ))}

      <div className="contacts__location">
        <span className="contacts__icon contacts__icon--muted" aria-hidden="true">
          <MapPin size={20} strokeWidth={2} />
        </span>
        <span className="contacts__body">
          <span className="contacts__label">Headquarters</span>
          <span className="contacts__value">{location}</span>
        </span>
      </div>
    </div>
  );
}
