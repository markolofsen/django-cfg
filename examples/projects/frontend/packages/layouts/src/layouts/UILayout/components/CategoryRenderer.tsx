/**
 * CategoryRenderer
 * Universal renderer for any category using config data
 */

'use client';

import React from 'react';
import { getComponentsByCategory, getCategoryById } from '../config';
import { AutoComponentDemo, CategorySection } from './AutoComponentDemo';

interface CategoryRendererProps {
  categoryId: string;
}

/**
 * CategoryRenderer - Dynamically renders all components in a category
 * No need for separate demo files - everything comes from config
 */
export function CategoryRenderer({ categoryId }: CategoryRendererProps) {
  const category = getCategoryById(categoryId);
  const components = getComponentsByCategory(categoryId);

  if (!category || components.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground">
        <p>No components found for this category</p>
      </div>
    );
  }

  return (
    <CategorySection
      title={category.label}
      description={category.description}
    >
      {components.map((component) => (
        <AutoComponentDemo
          key={component.name}
          component={component}
        />
      ))}
    </CategorySection>
  );
}
