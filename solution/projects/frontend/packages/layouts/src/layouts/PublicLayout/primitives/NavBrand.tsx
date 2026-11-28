'use client';

import React, { memo, type ReactNode } from 'react';

import { Link } from '@djangocfg/ui-core/components';

interface NavBrandProps {
  brand?: ReactNode;
  brandHref?: string;
}

function NavBrandRaw({ brand, brandHref = '/' }: NavBrandProps) {
  if (brand == null || brand === '' || brand === false) return null;

  if (typeof brand === 'string') {
    return (
      <Link
        href={brandHref}
        className="font-bold text-[15px] text-foreground hover:opacity-90 transition-opacity pointer-coarse:inline-flex pointer-coarse:min-h-11 pointer-coarse:items-center"
      >
        {brand}
      </Link>
    );
  }

  return <>{brand}</>;
}

export const NavBrand = memo(NavBrandRaw);
