/**
 * UI Guide View
 * Main view for showcasing all UI components from @djangocfg/ui package
 * Uses config-driven approach - all data comes from centralized config
 */

'use client';

import React from 'react';
import { UILayout } from './UILayout';
import { CATEGORIES } from './config';
import { ShowcaseProvider, useShowcase } from './context';
import { UIGuideLanding } from './UIGuideLanding';
import { CategoryRenderer } from './components/CategoryRenderer';
import { TailwindGuideRenderer } from './components/TailwindGuideRenderer';

function UIGuideContent() {
  const { currentCategory, setCurrentCategory } = useShowcase();

  // For overview, show only landing page without layout
  if (currentCategory === 'overview') {
    return <UIGuideLanding />;
  }

  // Logo component
  const logo = (
    <div className="h-8 w-8 rounded-md bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
      DC
    </div>
  );

  return (
    <UILayout
      title="UI Component Library"
      description="Explore our comprehensive collection of 56+ React components built with Radix UI and Tailwind CSS"
      categories={CATEGORIES}
      currentCategory={currentCategory}
      onCategoryChange={setCurrentCategory}
      logo={logo}
      projectName="Django CFG UI"
    >
      <div className="space-y-8">
        {/* Tailwind 4 Guide */}
        {currentCategory === 'tailwind4' && <TailwindGuideRenderer />}

        {/* All other categories use CategoryRenderer */}
        {currentCategory !== 'tailwind4' && currentCategory !== 'overview' && (
          <CategoryRenderer categoryId={currentCategory} />
        )}
      </div>
    </UILayout>
  );
}

export default function UIGuideView() {
  return (
    <ShowcaseProvider defaultCategory="overview">
      <UIGuideContent />
    </ShowcaseProvider>
  );
}
