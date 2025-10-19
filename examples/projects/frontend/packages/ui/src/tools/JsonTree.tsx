import React, { useState } from 'react';
import { CommonExternalProps, JSONTree } from 'react-json-tree';
import { ChevronDown, ChevronRight, Copy, Download } from 'lucide-react';
import { Button } from '../components/button';

export type { Language } from 'prism-react-renderer';

export interface JsonTreeConfig {
  /** Maximum depth to expand automatically (default: 2) */
  maxAutoExpandDepth?: number;
  /** Maximum items in array to auto-expand (default: 10) */
  maxAutoExpandArrayItems?: number;
  /** Maximum object keys to auto-expand (default: 5) */
  maxAutoExpandObjectKeys?: number;
  /** Maximum string length before truncation (default: 200) */
  maxStringLength?: number;
  /** Collection limit for performance (default: 50) */
  collectionLimit?: number;
  /** Whether to show collection info (array length, object keys count) */
  showCollectionInfo?: boolean;
  /** Whether to show expand/collapse all buttons */
  showExpandControls?: boolean;
  /** Whether to show copy/download buttons */
  showActionButtons?: boolean;
  /** Custom CSS classes for the container */
  className?: string;
  /** Whether to preserve object key order (default: true) */
  preserveKeyOrder?: boolean;
}

interface JsonTreeComponentProps {
  title?: string;
  data: unknown;
  config?: JsonTreeConfig;
  /** Override for react-json-tree props */
  jsonTreeProps?: Partial<CommonExternalProps>;
}

const JsonTreeComponent = ({ title, data, config = {}, jsonTreeProps = {} }: JsonTreeComponentProps) => {
  // State for expand/collapse all
  const [expandAll, setExpandAll] = useState(false);
  const [renderKey, setRenderKey] = useState(0);
  
  // Default configuration
  const {
    maxAutoExpandDepth = 2,
    maxAutoExpandArrayItems = 10,
    maxAutoExpandObjectKeys = 5,
    maxStringLength = 200,
    collectionLimit = 50,
    showCollectionInfo = true,
    showExpandControls = true,
    showActionButtons = true,
    className = '',
    preserveKeyOrder = true,
  } = config;
  
  // Get CSS variables for semantic colors and convert to hsl format
  const getCSSVariable = (variable: string) => {
    if (typeof document === 'undefined') return '';
    const value = getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
    return value ? `hsl(${value})` : '';
  };

  // JSON Tree theme using only available semantic Tailwind colors
  const jsonTreeTheme = {
    scheme: 'monokai',
    base00: 'transparent', // Background - transparent to inherit from parent
    base01: getCSSVariable('--muted'), // Muted background
    base02: getCSSVariable('--border'), // Border
    base03: getCSSVariable('--muted-foreground'), // Muted text
    base04: getCSSVariable('--muted-foreground'), // Secondary text
    base05: getCSSVariable('--foreground'), // Main text
    base06: getCSSVariable('--foreground'), // Primary text
    base07: getCSSVariable('--foreground'), // Bright text
    base08: getCSSVariable('--destructive'), // Red/Error
    base09: getCSSVariable('--accent'), // Orange → use accent
    base0A: getCSSVariable('--primary'), // Yellow → use primary
    base0B: getCSSVariable('--secondary'), // Green → use secondary
    base0C: getCSSVariable('--primary'), // Cyan → use primary
    base0D: getCSSVariable('--primary'), // Blue/Primary
    base0E: getCSSVariable('--secondary'), // Magenta/Secondary
    base0F: getCSSVariable('--accent'), // Light red/Accent
  };

  // Smart expansion logic
  const shouldExpandNodeInitially = (keyPath: readonly (string | number)[], nodeData: unknown, level: number) => {
    // If user clicked "Expand All", expand everything
    if (expandAll) return true;
    
    // If user clicked "Collapse All", collapse everything except root level
    if (expandAll === false && level > 0) return false;
    
    // Always expand up to maxAutoExpandDepth
    if (level <= maxAutoExpandDepth) return true;
    
    // For arrays, expand if they have less than maxAutoExpandArrayItems
    if (Array.isArray(nodeData) && nodeData.length <= maxAutoExpandArrayItems) return true;
    
    // For objects, expand if they have less than maxAutoExpandObjectKeys
    if (nodeData && typeof nodeData === 'object' && !Array.isArray(nodeData)) {
      const keys = Object.keys(nodeData);
      return keys.length <= maxAutoExpandObjectKeys;
    }
    
    return false;
  };

  // Collection info display
  const getItemString = showCollectionInfo 
    ? (nodeType: string, nodeData: unknown) => {
        if (nodeType === 'Array') {
          const length = Array.isArray(nodeData) ? nodeData.length : 0;
          return length > 0 ? <span className="text-muted-foreground text-sm">({length} items)</span> : null;
        }
        if (nodeType === 'Object') {
          const keys = nodeData && typeof nodeData === 'object' ? Object.keys(nodeData) : [];
          return keys.length > 0 ? <span className="text-muted-foreground text-sm">({keys.length} keys)</span> : null;
        }
        return null;
      }
    : () => null;

  // Value processing for better display
  const postprocessValue = (value: unknown) => {
    // Truncate very long strings
    if (typeof value === 'string' && value.length > maxStringLength) {
      return value.substring(0, maxStringLength) + '... (truncated)';
    }
    return value;
  };

  // Custom node detection for special formatting
  const isCustomNode = (value: unknown) => {
    // Mark URLs as custom nodes for special styling
    if (typeof value === 'string' && (value.startsWith('http://') || value.startsWith('https://'))) {
      return true;
    }
    return false;
  };

  // Action handlers
  const handleCopy = () => {
    const jsonString = JSON.stringify(data, null, 2);
    navigator.clipboard.writeText(jsonString);
  };

  const handleDownload = () => {
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'data.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`relative border border-border rounded-sm h-full overflow-hidden ${className}`}>
      {/* Header with title and controls */}
      {(title || showExpandControls || showActionButtons) && (
        <div className="p-4 border-b border-border bg-muted/50 rounded-t-sm">
          <div className="flex items-center justify-between">
            {title && (
              <h6 className="text-lg font-semibold text-foreground">{title}</h6>
            )}
            
            {(showExpandControls || showActionButtons) && (
              <div className="flex items-center space-x-2">
                {/* Expand/Collapse Controls */}
                {showExpandControls && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setExpandAll(!expandAll);
                      setRenderKey(prev => prev + 1);
                    }}
                    className="h-8 px-2"
                  >
                    {expandAll ? (
                      <>
                        <ChevronRight className="h-3 w-3" />
                        <span className="ml-1 text-xs">Collapse All</span>
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-3 w-3" />
                        <span className="ml-1 text-xs">Expand All</span>
                      </>
                    )}
                  </Button>
                )}
                
                {/* Action Buttons */}
                {showActionButtons && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCopy}
                      className="h-8 px-2"
                    >
                      <Copy className="h-3 w-3" />
                      <span className="ml-1 text-xs hidden sm:inline">Copy</span>
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleDownload}
                      className="h-8 px-2"
                    >
                      <Download className="h-3 w-3" />
                      <span className="ml-1 text-xs hidden sm:inline">Download</span>
                    </Button>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* JSON Tree Content */}
      <div className="h-full overflow-auto p-4">
        <JSONTree
          key={renderKey} // Force re-render when expand/collapse state changes
          data={data}
          theme={jsonTreeTheme}
          invertTheme={false}
          hideRoot={true}
          shouldExpandNodeInitially={shouldExpandNodeInitially}
          getItemString={getItemString}
          postprocessValue={postprocessValue}
          isCustomNode={isCustomNode}
          collectionLimit={collectionLimit}
          sortObjectKeys={!preserveKeyOrder}
          {...jsonTreeProps}
        />
      </div>
    </div>
  );
};

export default JsonTreeComponent; 