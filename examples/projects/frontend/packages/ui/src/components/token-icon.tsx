"use client"

import * as React from "react"
import { TokenIcon as Web3TokenIcon } from '@web3icons/react'
import { cn } from "../lib/utils"

export interface TokenIconProps extends React.HTMLAttributes<HTMLDivElement> {
  symbol: string
  variant?: 'branded' | 'mono'
  size?: number
  network?: string
  address?: string
}

export function TokenIcon({
  symbol,
  variant = 'branded',
  size = 24,
  className,
  network,
  address,
  ...props
}: TokenIconProps) {
  // Ensure symbol is a string and lowercase for @web3icons/react
  const symbolStr = symbol ? String(symbol).toLowerCase() : 'unknown'

  return (
    <div
      className={cn("inline-flex items-center justify-center flex-shrink-0", className)}
      style={{ width: size, height: size }}
      {...props}
    >
      {network && address ? (
        <Web3TokenIcon
          network={network as any}
          address={address}
          variant={variant}
          size={size.toString()}
        />
      ) : (
        <Web3TokenIcon
          symbol={symbolStr}
          variant={variant}
          size={size.toString()}
        />
      )}
    </div>
  )
}
