/**
 * Tailwind CSS v4 Configuration & Guidelines
 * Documentation for Tailwind CSS v4 best practices
 */

export interface TailwindGuide {
  version: string;
  keyChanges: string[];
  bestPractices: string[];
  migrationSteps: string[];
  examples: {
    title: string;
    description: string;
    code: string;
  }[];
}

export const TAILWIND_GUIDE: TailwindGuide = {
  version: "4.0",

  keyChanges: [
    "CSS-First Configuration: Theme is now defined using CSS custom properties in an @theme block instead of JavaScript",
    "New Import Syntax: Use @import \"tailwindcss\" instead of @tailwind directives",
    "Simplified PostCSS Setup: Use @tailwindcss/postcss plugin",
    "Performance Improvements: 10x faster build times, significantly smaller CSS bundles",
    "Modern Browser Support: Optimized for Safari 16.4+, Chrome 111+, Firefox 128+"
  ],

  bestPractices: [
    "Use standard Tailwind classes only: py-16 sm:py-20 md:py-24 lg:py-32",
    "Responsive patterns: px-4 sm:px-6 lg:px-8",
    "Container pattern: container max-w-7xl mx-auto",
    "Avoid custom utilities like: section-padding, animate-*, shadow-brand",
    "Mobile-first approach with breakpoints: sm: (640px), md: (768px), lg: (1024px), xl: (1280px)",
    "Use CSS variables: var(--color-primary), var(--font-family-sans)"
  ],

  migrationSteps: [
    "Update dependencies: npm install tailwindcss@latest postcss@latest",
    "Replace JavaScript config with CSS @theme block",
    "Update import directives: @import \"tailwindcss\"",
    "Configure PostCSS: use @tailwindcss/postcss plugin",
    "Test and refactor: remove custom utilities and use standard Tailwind classes"
  ],

  examples: [
    {
      title: "CSS-First Configuration",
      description: "Define theme using CSS custom properties",
      code: `@import "tailwindcss";

@theme {
  --color-primary: #3b82f6;
  --color-secondary: #8b5cf6;
  --font-family-sans: ui-sans-serif, system-ui, sans-serif;
}`
    },
    {
      title: "Responsive Spacing",
      description: "Mobile-first responsive padding and spacing",
      code: `<section className="py-16 sm:py-20 md:py-24 lg:py-32">
  <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl">
      Title
    </h1>
  </div>
</section>`
    },
    {
      title: "Component Styling",
      description: "Standard Tailwind classes for components",
      code: `<button className="px-6 py-3 bg-primary text-primary-foreground rounded-md shadow-lg hover:shadow-xl transition-all duration-300">
  Click me
</button>`
    }
  ]
};
