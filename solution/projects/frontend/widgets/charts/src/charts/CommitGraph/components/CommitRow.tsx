// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';


import * as React from 'react';
import { alpha } from '@djangocfg/ui-core/styles/palette';
import { ROW_HEIGHT, type GraphRow } from '../types';
import { formatRelativeDate, initials } from '../utils';
import { CommitDetail } from './CommitDetail';
import { Rails } from './Rails';

interface CommitRowProps {
  row: GraphRow;
  prevRow: GraphRow | null;
  railWidth: number;
  maxRails: number;
  truncateHash: number;
  laneColors: string[];
  railColor: string;
}

/**
 * Single commit row: rails column, refs, message, hash + author + time.
 * Wrapped in a {@link CommitDetail} popover.
 */
export function CommitRow({
  row,
  prevRow,
  railWidth,
  maxRails,
  truncateHash,
  laneColors,
  railColor,
}: CommitRowProps) {
  const svgWidth = maxRails * railWidth;
  const refStyle = {
    borderColor: alpha(railColor, 0.25),
    backgroundColor: alpha(railColor, 0.0625),
    color: railColor,
  };
  const tagStyle = {
    backgroundColor: alpha(railColor, 0.125),
    color: railColor,
  };
  const initialsLabel = initials(row.commit.author.name);
  const shortHash = row.commit.hash.slice(0, truncateHash);
  const relativeDate = formatRelativeDate(row.commit.date);

  return (
    <CommitDetail commit={row.commit} hashLength={truncateHash} railColor={railColor}>
      <button
        type="button"
        data-slot="commit-entry"
        className="flex w-full items-center gap-0 border-b border-border/30 transition-colors hover:bg-muted/30 focus-visible:bg-muted/30 focus-visible:outline-none last:border-b-0"
        style={{ height: ROW_HEIGHT }}
      >
        {/* Rails */}
        <div style={{ width: svgWidth }} className="shrink-0">
          <Rails
            row={row}
            prevRow={prevRow}
            railWidth={railWidth}
            maxRails={maxRails}
            laneColors={laneColors}
          />
        </div>

        {/* Refs + tag */}
        <div className="flex shrink-0 items-center gap-1 px-2">
          {row.commit.refs?.map((ref) => (
            <span
              key={ref}
              className="inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-[10px] font-semibold leading-none"
              style={refStyle}
            >
              {ref}
            </span>
          ))}
          {row.commit.tag && (
            <span
              className="inline-flex items-center rounded-md px-1.5 py-0.5 text-[10px] font-semibold leading-none"
              style={tagStyle}
            >
              {row.commit.tag}
            </span>
          )}
        </div>

        {/* Message */}
        <p className="min-w-0 flex-1 truncate px-2 text-left text-sm text-foreground/80">
          {row.commit.message}
        </p>

        {/* Meta */}
        <div className="flex shrink-0 items-center gap-3 px-3">
          <code className="font-mono text-[11px] text-muted-foreground/60">
            {shortHash}
          </code>
          <span className="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
            {row.commit.author.avatarUrl ? (
              <img
                src={row.commit.author.avatarUrl}
                alt=""
                width={16}
                height={16}
                className="size-4 rounded-full border border-border/60 bg-muted"
              />
            ) : (
              <span className="flex size-4 items-center justify-center rounded-full bg-muted text-[8px] font-bold text-muted-foreground">
                {initialsLabel}
              </span>
            )}
            <span className="hidden sm:inline">{row.commit.author.name}</span>
          </span>
          <span className="text-[11px] text-muted-foreground/50">{relativeDate}</span>
        </div>
      </button>
    </CommitDetail>
  );
}
