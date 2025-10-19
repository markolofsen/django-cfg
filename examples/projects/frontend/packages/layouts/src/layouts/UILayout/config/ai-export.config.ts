/**
 * AI Export Configuration
 * Generates formatted documentation for AI consumption
 */

import { COMPONENTS_CONFIG, getAllCategories } from './components';
import { TAILWIND_GUIDE } from './tailwind.config';

export interface UILibraryConfig {
  projectName: string;
  version: string;
  description: string;
  totalComponents: number;
}

export const UI_LIBRARY_CONFIG: UILibraryConfig = {
  projectName: "Django CFG UI",
  version: "1.0.0",
  description: "Comprehensive React UI library with 56+ components, 7 blocks, and 11 hooks built with Radix UI, Tailwind CSS v4, and TypeScript",
  totalComponents: COMPONENTS_CONFIG.length,
};

/**
 * Generate formatted text for AI consumption
 * This is the single source of truth that gets copied to clipboard
 */
export function generateAIContext(): string {
  const { projectName, version, description } = UI_LIBRARY_CONFIG;

  let output = `# ${projectName} v${version}\n\n`;
  output += `${description}\n\n`;

  // Tailwind 4 Guide
  output += `## Tailwind CSS v${TAILWIND_GUIDE.version} Guidelines\n\n`;

  output += `### Key Changes\n`;
  TAILWIND_GUIDE.keyChanges.forEach(change => {
    output += `- ${change}\n`;
  });
  output += `\n`;

  output += `### Best Practices\n`;
  TAILWIND_GUIDE.bestPractices.forEach(practice => {
    output += `- ${practice}\n`;
  });
  output += `\n`;

  output += `### Migration Steps\n`;
  TAILWIND_GUIDE.migrationSteps.forEach((step, index) => {
    output += `${index + 1}. ${step}\n`;
  });
  output += `\n`;

  output += `### Examples\n\n`;
  TAILWIND_GUIDE.examples.forEach(example => {
    output += `#### ${example.title}\n`;
    output += `${example.description}\n\n`;
    output += `\`\`\`css\n${example.code}\n\`\`\`\n\n`;
  });

  // Components by Category
  const categories = getAllCategories();

  categories.forEach(category => {
    const comps = COMPONENTS_CONFIG.filter(comp => comp.category === category);

    output += `## ${category.charAt(0).toUpperCase() + category.slice(1)} (${comps.length})\n\n`;

    comps.forEach(comp => {
      output += `### ${comp.name}\n`;
      output += `${comp.description}\n\n`;
      output += `\`\`\`tsx\n`;
      output += `${comp.importPath}\n\n`;
      output += `${comp.example}\n`;
      output += `\`\`\`\n\n`;
    });
  });

  return output;
}
