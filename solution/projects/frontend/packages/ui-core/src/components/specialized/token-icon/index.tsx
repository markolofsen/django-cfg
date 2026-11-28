"use client"

import * as React from 'react';

import { cn } from '../../../lib/utils';
import { touchSafeFontSize } from '../../../utils/touch-safe';

export interface TokenIconProps extends React.HTMLAttributes<HTMLDivElement> {
  symbol: string
  variant?: 'branded' | 'mono'
  size?: number
  network?: string
  address?: string
}

/**
 * Get all available token symbols from @web3icons/react
 * Uses dynamic import to avoid bundling all icons
 */
export async function getAllTokenSymbols(): Promise<string[]> {
  try {
    const { tokenIcons } = await import('@web3icons/react')
    return Object.keys(tokenIcons).map(key => 
      key.replace(/^Token/, '').replace(/_/g, '-')
    ).sort()
  } catch {
    return []
  }
}

/**
 * Search tokens by symbol
 */
export async function searchTokens(query: string): Promise<string[]> {
  const allTokens = await getAllTokenSymbols()
  const lowerQuery = query.toLowerCase()
  return allTokens.filter(symbol => 
    symbol.toLowerCase().includes(lowerQuery)
  )
}

/**
 * Get popular tokens grouped by category
 */
export interface TokenCategory {
  name: string
  tokens: string[]
}

export async function getTokensByCategory(): Promise<TokenCategory[]> {
  const allTokens = await getAllTokenSymbols()
  
  // Top tokens by market cap
  const topTokens = ['BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'USDC', 'XRP', 'DOGE', 'ADA', 'TRX']
    .filter(t => allTokens.includes(t))
  
  const stablecoins = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDP', 'GUSD', 'FRAX']
    .filter(t => allTokens.includes(t))
  
  const defi = ['UNI', 'AAVE', 'MKR', 'CRV', 'CAKE', 'SUSHI', 'BAL', 'COMP', 'YFI', 'SNX', 'LINK']
    .filter(t => allTokens.includes(t))
  
  const layer1 = ['ETH', 'BNB', 'SOL', 'ADA', 'AVAX', 'DOT', 'ATOM', 'NEAR', 'ALGO', 'FTM']
    .filter(t => allTokens.includes(t))
  
  const layer2 = ['MATIC', 'OP', 'ARB', 'IMX', 'LRC', 'METIS']
    .filter(t => allTokens.includes(t))
  
  const memeCoins = ['DOGE', 'SHIB', 'PEPE', 'FLOKI', 'ELON', 'BONK']
    .filter(t => allTokens.includes(t))
  
  return [
    { name: 'Top 10', tokens: topTokens },
    { name: 'Stablecoins', tokens: stablecoins },
    { name: 'DeFi', tokens: defi },
    { name: 'Layer 1', tokens: layer1 },
    { name: 'Layer 2', tokens: layer2 },
    { name: 'Meme Coins', tokens: memeCoins },
  ].filter(cat => cat.tokens.length > 0)
}

export type TokenSymbol = string

/** The only props this file passes to a resolved @web3icons component. */
type TokenIconComponent = React.ComponentType<{
  variant?: 'branded' | 'mono'
  size?: number
}>

// Dynamic import for @web3icons/react tokens
const tokenIconCache = new Map<string, TokenIconComponent>()

async function getTokenIcon(symbol: string): Promise<TokenIconComponent | null> {
  const normalizedSymbol = symbol.toUpperCase().replace(/[^A-Z0-9]/g, '_')
  const componentName = `Token${normalizedSymbol}`

  const cached = tokenIconCache.get(componentName)
  if (cached) {
    return cached
  }

  try {
    // The export name is computed at runtime, so the module is read as an
    // untyped key map and the value is proven to be a component (a function)
    // before it is used.
    const namespace: Record<string, unknown> = await import('@web3icons/react')
    const Component = namespace[componentName]
    if (typeof Component === 'function') {
      const IconComponent = Component as TokenIconComponent
      tokenIconCache.set(componentName, IconComponent)
      return IconComponent
    }
  } catch (_e) {
    // Token not found
  }

  return null
}

export function TokenIcon({
  symbol,
  variant = 'branded',
  size = 24,
  className,
  // Destructured, not used: these narrow which icon is resolved upstream
  // and must not fall through `...props` onto the DOM element below.
  network: _network,
  address: _address,
  ...props
}: TokenIconProps) {
  const [IconComponent, setIconComponent] = React.useState<TokenIconComponent | null>(null)
  const [_loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    let mounted = true

    getTokenIcon(symbol).then((component) => {
      if (mounted) {
        setIconComponent(() => component)
        setLoading(false)
      }
    })

    return () => {
      mounted = false
    }
  }, [symbol])

  // Pre-compute fallback values
  const fallbackFontSize = Math.max(8, size * 0.4)
  const truncatedSymbol = symbol?.slice(0, 3) || '?'

  // Touch-safe font size for iOS auto-zoom prevention
  // iOS: max(16px, fallbackFontSize), Android/Desktop: fallbackFontSize
  const touchSafeFallbackFontSize = touchSafeFontSize(`${fallbackFontSize}px`)

  return (
    <div
      className={cn("inline-flex items-center justify-center flex-shrink-0", className)}
      style={{ width: size, height: size }}
      {...props}
    >
      {IconComponent ? (
        <IconComponent
          variant={variant}
          size={size}
        />
      ) : (
        // Fallback: show symbol as text
        <span
          className="text-muted-foreground font-medium uppercase"
          style={{ fontSize: touchSafeFallbackFontSize }}
        >
          {truncatedSymbol}
        </span>
      )}
    </div>
  )
}
