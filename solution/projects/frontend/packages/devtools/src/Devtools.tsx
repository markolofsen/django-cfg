'use client'

/**
 * <Devtools /> — the one component.
 *
 * Drop it once into the app root; it installs error/console capture with
 * backend ingest AND renders the floating debug button + panel. Replaces the
 * old MonitorProvider + DebugButton + monitorBridge trio.
 *
 * @example
 * // app/layout.tsx (or BaseApp)
 * import { Devtools } from '@djangocfg/devtools'
 *
 * <Devtools project="my-app" environment={process.env.NODE_ENV} />
 */

import React, { memo, useEffect } from 'react'

import { devtools } from './instance'
import { DevtoolsButton } from './panel/DevtoolsButton'
import type { DevtoolsPanelProps } from './panel/DevtoolsPanel'
import type { DevtoolsConfig } from './types'

export interface DevtoolsProps extends DevtoolsConfig {
  /** Panel customization (custom tabs, position, size) */
  panel?: DevtoolsPanelProps
  /** Hide the debug button entirely (capture + ingest still run). `?debug=1` overrides. */
  button?: boolean
  children?: React.ReactNode
}

function DevtoolsRaw({ panel, button, children, ...config }: DevtoolsProps) {
  useEffect(() => {
    devtools.init(config)
    return () => devtools.destroy()
    // Init once per mount — config is captured in the closure.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <>
      {children}
      <DevtoolsButton enabled={button} panel={panel} />
    </>
  )
}

export const Devtools = memo(DevtoolsRaw)
