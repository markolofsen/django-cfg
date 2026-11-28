'use client';

import { useCallback, useMemo, useState } from 'react';

export interface UseCollapsibleContentOptions {
  /**
   * Maximum character length before collapsing
   * If both maxLength and maxLines are set, the stricter limit applies
   */
  maxLength?: number;
  /**
   * Maximum number of lines before collapsing
   * If both maxLength and maxLines are set, the stricter limit applies
   */
  maxLines?: number;
  /**
   * Start in expanded state (default: false - starts collapsed)
   */
  defaultExpanded?: boolean;
}

export interface UseCollapsibleContentResult {
  /** Whether content is currently collapsed */
  isCollapsed: boolean;
  /** Toggle between collapsed/expanded state */
  toggleCollapsed: () => void;
  /** Set collapsed state directly */
  setCollapsed: (collapsed: boolean) => void;
  /** Content to display (truncated if collapsed, full if expanded) */
  displayContent: string;
  /** Whether the content exceeds limits and should be collapsible */
  shouldCollapse: boolean;
  /** Original content length */
  originalLength: number;
  /** Original line count */
  originalLineCount: number;
}

/**
 * Smart truncation that doesn't break words or markdown syntax
 */
function smartTruncate(content: string, maxLength: number): string {
  if (content.length <= maxLength) {
    return content;
  }

  // Find a good break point (space, newline) near maxLength
  let breakPoint = maxLength;

  // Look backwards for a space or newline
  while (breakPoint > maxLength - 50 && breakPoint > 0) {
    const char = content[breakPoint];
    if (char === ' ' || char === '\n' || char === '\t') {
      break;
    }
    breakPoint--;
  }

  // If we couldn't find a good break point, just use maxLength
  if (breakPoint <= maxLength - 50) {
    breakPoint = maxLength;
  }

  let truncated = content.slice(0, breakPoint).trimEnd();

  // Fix unclosed markdown syntax
  truncated = fixUnclosedMarkdown(truncated);

  return truncated;
}

/**
 * Truncate by line count
 */
function truncateByLines(content: string, maxLines: number): string {
  const lines = content.split('\n');

  if (lines.length <= maxLines) {
    return content;
  }

  let truncated = lines.slice(0, maxLines).join('\n').trimEnd();

  // Fix unclosed markdown syntax
  truncated = fixUnclosedMarkdown(truncated);

  return truncated;
}

/**
 * Fix unclosed markdown syntax to prevent rendering issues
 */
function fixUnclosedMarkdown(content: string): string {
  let result = content;

  // Count occurrences of markdown markers
  const countOccurrences = (str: string, marker: string): number => {
    const escaped = marker.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const matches = str.match(new RegExp(escaped, 'g'));
    return matches ? matches.length : 0;
  };

  // Fix unclosed bold (**) - must have even count
  const boldCount = countOccurrences(result, '**');
  if (boldCount % 2 !== 0) {
    result += '**';
  }

  // Fix unclosed italic (*) - but not **
  // Remove ** first for counting, then count single *
  const withoutBold = result.replace(/\*\*/g, '');
  const italicCount = countOccurrences(withoutBold, '*');
  if (italicCount % 2 !== 0) {
    result += '*';
  }

  // Fix unclosed inline code (`)
  const codeCount = countOccurrences(result, '`');
  // Ignore triple backticks for code blocks
  const tripleCount = countOccurrences(result, '```');
  const singleCodeCount = codeCount - (tripleCount * 3);
  if (singleCodeCount % 2 !== 0) {
    result += '`';
  }

  // Fix unclosed code blocks (```)
  if (tripleCount % 2 !== 0) {
    result += '\n```';
  }

  // Fix unclosed strikethrough (~~)
  const strikeCount = countOccurrences(result, '~~');
  if (strikeCount % 2 !== 0) {
    result += '~~';
  }

  // Fix unclosed underline bold (__)
  const underlineBoldCount = countOccurrences(result, '__');
  if (underlineBoldCount % 2 !== 0) {
    result += '__';
  }

  // Fix unclosed underline italic (_) - but not __
  const withoutUnderlineBold = result.replace(/__/g, '');
  const underlineItalicCount = countOccurrences(withoutUnderlineBold, '_');
  if (underlineItalicCount % 2 !== 0) {
    result += '_';
  }

  return result;
}

/**
 * Hook for managing collapsible content with "Read more..." functionality
 *
 * @example
 * ```tsx
 * const { isCollapsed, toggleCollapsed, displayContent, shouldCollapse } = useCollapsibleContent(
 *   longText,
 *   { maxLength: 300, maxLines: 5 }
 * );
 *
 * return (
 *   <div>
 *     <Markdown content={displayContent} />
 *     {shouldCollapse && (
 *       <button onClick={toggleCollapsed}>
 *         {isCollapsed ? 'Read more...' : 'Show less'}
 *       </button>
 *     )}
 *   </div>
 * );
 * ```
 */
export function useCollapsibleContent(
  content: string,
  options: UseCollapsibleContentOptions = {}
): UseCollapsibleContentResult {
  const { maxLength, maxLines, defaultExpanded = false } = options;

  const [isCollapsed, setIsCollapsed] = useState(!defaultExpanded);

  const originalLength = content.length;
  const originalLineCount = content.split('\n').length;

  const { shouldCollapse, truncatedContent } = useMemo(() => {
    // If no limits set, don't collapse
    if (maxLength === undefined && maxLines === undefined) {
      return { shouldCollapse: false, truncatedContent: content };
    }

    let needsCollapse = false;
    let result = content;

    // Check line limit first (usually more restrictive for chat)
    if (maxLines !== undefined && originalLineCount > maxLines) {
      needsCollapse = true;
      result = truncateByLines(result, maxLines);
    }

    // Then check character limit
    if (maxLength !== undefined && result.length > maxLength) {
      needsCollapse = true;
      result = smartTruncate(result, maxLength);
    }

    return { shouldCollapse: needsCollapse, truncatedContent: result };
  }, [content, maxLength, maxLines, originalLineCount]);

  const displayContent = useMemo(() => {
    if (!shouldCollapse || !isCollapsed) {
      return content;
    }
    return truncatedContent;
  }, [content, truncatedContent, shouldCollapse, isCollapsed]);

  const toggleCollapsed = useCallback(() => {
    setIsCollapsed((prev) => !prev);
  }, []);

  const setCollapsed = useCallback((collapsed: boolean) => {
    setIsCollapsed(collapsed);
  }, []);

  return {
    isCollapsed,
    toggleCollapsed,
    setCollapsed,
    displayContent,
    shouldCollapse,
    originalLength,
    originalLineCount,
  };
}

export default useCollapsibleContent;
