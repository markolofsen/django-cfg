/**
 * Optional slots around the nav groups: menuStart, featured, menuEnd, footer.
 */

'use client';

import React, { memo } from 'react';

import { usePrivateLayoutContext } from '../context';
import { SidebarFeatured } from './SidebarFeatured';

function SidebarSlotsRaw() {
  const { sidebar, geometry } = usePrivateLayoutContext();
  if (!sidebar) return null;
  const SLOT = `w-full min-w-0 shrink-0 ${geometry.inset}`;

  return (
    <>
      {sidebar.menuStart ? <div className={SLOT}>{sidebar.menuStart}</div> : null}
      {sidebar.featured ? (
        <div className={SLOT}>
          <SidebarFeatured config={sidebar.featured} />
        </div>
      ) : null}
      {sidebar.menuEnd ? <div className={SLOT}>{sidebar.menuEnd}</div> : null}
      {sidebar.footer ? <div className={SLOT}>{sidebar.footer}</div> : null}
    </>
  );
}

export const SidebarSlots = memo(SidebarSlotsRaw);
