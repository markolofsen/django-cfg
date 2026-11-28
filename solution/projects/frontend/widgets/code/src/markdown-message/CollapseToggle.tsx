import React, { memo } from 'react';

import { TOGGLE } from '../role-tokens';

interface CollapseToggleProps {
  isCollapsed: boolean;
  onClick: () => void;
  readMoreLabel: string;
  showLessLabel: string;
  isUser: boolean;
  isCompact: boolean;
}

/** "Read more..." / "Show less" button.
 *
 * Memoised: re-renders only when `isCollapsed`, `onClick`, `readMoreLabel`,
 * `showLessLabel`, `isUser` or `isCompact` change. `onClick` is compared
 * by reference — callers should stabilise it with useCallback.
 */
function CollapseToggleRaw({
  isCollapsed,
  onClick,
  readMoreLabel,
  showLessLabel,
  isUser,
  isCompact,
}: CollapseToggleProps) {
  const textSize = isCompact ? 'text-xs' : 'text-sm';
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        ${textSize} font-medium cursor-pointer
        transition-colors duration-200
        ${isUser ? TOGGLE.user : TOGGLE.assistant}
        inline-flex items-center gap-1
        mt-1
      `}
    >
      {isCollapsed ? (
        <>
          {readMoreLabel}
          <Chevron direction="down" />
        </>
      ) : (
        <>
          {showLessLabel}
          <Chevron direction="up" />
        </>
      )}
    </button>
  );
};

const Chevron = memo(function Chevron({ direction }: { direction: 'up' | 'down' }) {
  return (
    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d={direction === 'down' ? 'M19 9l-7 7-7-7' : 'M5 15l7-7 7 7'}
      />
    </svg>
  );
});

export const CollapseToggle = memo(CollapseToggleRaw);
