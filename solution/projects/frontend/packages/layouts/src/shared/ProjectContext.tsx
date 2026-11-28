/**
 * The project name `BaseApp` already receives (`project` prop), exposed to descendants so shells can use it as the
 * default product name. Outside `BaseApp` (stories, tests) the hook returns `undefined` and never throws.
 */

'use client';

import React from 'react';

const ProjectNameContext = React.createContext<string | undefined>(undefined);

export function ProjectNameProvider({ value, children }: { value?: string; children: React.ReactNode }) {
  return <ProjectNameContext.Provider value={value?.trim() || undefined}>{children}</ProjectNameContext.Provider>;
}

export function useProjectName(): string | undefined {
  return React.useContext(ProjectNameContext);
}
