'use client';

import React from 'react';

import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

export interface UserAvatarProps {
  src?: string;
  name: string;
  /** 'sm' = 32px (navbar), 'md' = 44px (drawer header). Defaults to 'sm'. */
  size?: 'sm' | 'md';
  className?: string;
}

const SIZE = {
  sm: { avatar: 'h-8 w-8', text: 'text-sm' },
  md: { avatar: 'h-11 w-11', text: 'text-base' },
} as const;

export function UserAvatar({ src, name, size = 'sm', className }: UserAvatarProps) {
  const initial = name.charAt(0).toUpperCase();
  const s = SIZE[size];

  return (
    <Avatar
      className={cn(
        s.avatar,
        'ring-2 ring-border/60 hover:ring-primary/70 transition-all shrink-0',
        className,
      )}
    >
      <AvatarImage src={src} alt={name} />
      <AvatarFallback
        className={cn(
          'bg-primary text-primary-foreground font-semibold',
          s.text,
        )}
      >
        {initial}
      </AvatarFallback>
    </Avatar>
  );
}
