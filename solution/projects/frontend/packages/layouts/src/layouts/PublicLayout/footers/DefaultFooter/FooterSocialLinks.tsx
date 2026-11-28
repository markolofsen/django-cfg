'use client';

import { Mail, MessageCircle, MessageSquare } from 'lucide-react';
import React from 'react';

import {
  FacebookIcon, GithubIcon, InstagramIcon, LinkedinIcon, TwitterIcon, YoutubeIcon,
} from './brandIcons';

import type { FooterSocialLinks } from './types';

export interface FooterSocialLinksProps {
  socialLinks?: FooterSocialLinks;
  className?: string;
  iconClassName?: string;
}

const socialIconsMap = {
  github: { icon: GithubIcon, title: 'GitHub' },
  linkedin: { icon: LinkedinIcon, title: 'LinkedIn' },
  twitter: { icon: TwitterIcon, title: 'Twitter' },
  telegram: { icon: MessageCircle, title: 'Telegram' },
  youtube: { icon: YoutubeIcon, title: 'YouTube' },
  facebook: { icon: FacebookIcon, title: 'Facebook' },
  instagram: { icon: InstagramIcon, title: 'Instagram' },
  whatsapp: { icon: MessageSquare, title: 'WhatsApp' },
  email: { icon: Mail, title: 'Email' },
} as const;

export function FooterSocialLinksComponent({
  socialLinks,
  className = 'flex space-x-4',
  iconClassName = 'w-5 h-5',
}: FooterSocialLinksProps) {
  const socialLinksData = socialLinks
    ? Object.entries(socialLinks)
        .filter(([_, url]) => url)
        .map(([platform, url]) => {
          const social = socialIconsMap[platform as keyof typeof socialIconsMap];
          if (!social) return null;
          return {
            platform,
            url: url!,
            icon: social.icon,
            title: social.title,
          };
        })
        .filter((item): item is NonNullable<typeof item> => item !== null)
    : [];

  if (socialLinksData.length === 0) return null;

  return (
    <div className={className}>
      {socialLinksData.map((social) => {
        const Icon = social.icon;
        return (
          <a
            key={social.platform}
            href={social.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-primary transition-colors"
            title={social.title}
          >
            <Icon className={iconClassName} />
          </a>
        );
      })}
    </div>
  );
}
