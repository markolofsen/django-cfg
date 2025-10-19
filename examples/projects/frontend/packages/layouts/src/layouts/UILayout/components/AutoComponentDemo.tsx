/**
 * AutoComponentDemo
 * Automatically renders component demos from configuration
 */

'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Tabs, TabsContent, TabsList, TabsTrigger } from '@djangocfg/ui';
import { PrettyCode } from '@djangocfg/ui/tools';
import type { ComponentConfig } from '../config';

interface AutoComponentDemoProps {
  component: ComponentConfig;
}

/**
 * AutoComponentDemo - Renders a component demo from config
 * This is the single component used to display all UI components
 */
export function AutoComponentDemo({ component }: AutoComponentDemoProps) {
  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-lg">{component.name}</CardTitle>
        <CardDescription>{component.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="preview" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="preview">Preview</TabsTrigger>
            <TabsTrigger value="code">Code</TabsTrigger>
          </TabsList>

          <TabsContent value="preview" className="space-y-4">
            <div className="p-6 border rounded-md bg-card">
              {component.preview}
            </div>
          </TabsContent>

          <TabsContent value="code">
            <PrettyCode
              data={`${component.importPath}\n\n${component.example}`}
              language="tsx"
              className="text-sm"
            />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

/**
 * CategorySection - Groups related component demos
 */
interface CategorySectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export function CategorySection({ title, description, children }: CategorySectionProps) {
  return (
    <div className="mb-12">
      <div className="mb-6">
        <h2 className="text-2xl font-bold tracking-tight">{title}</h2>
        {description && (
          <p className="text-muted-foreground mt-2">{description}</p>
        )}
      </div>
      <div className="space-y-6">
        {children}
      </div>
    </div>
  );
}
