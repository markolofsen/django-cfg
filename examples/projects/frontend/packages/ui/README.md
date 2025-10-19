# @djangocfg/ui

Internal UI package with shared components, styles, and Tailwind configuration.

## What's Inside

- **Tailwind Config** - Universal preset with theme, colors, fonts
- **Global Styles** - CSS variables and base styles
- **Shared Components** - Common UI components

## Usage

### Import Styles

```tsx
import '@djangocfg/ui/styles';
```

### Use Tailwind Preset

```js
// tailwind.config.js
module.exports = {
  presets: [require('@djangocfg/ui/tailwind.config.js')],
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    // Add ui and layouts packages
    '../../packages/ui/src/**/*.{js,ts,jsx,tsx}',
    '../../packages/layouts/src/**/*.{js,ts,jsx,tsx}',
  ],
};
```

## Features

- **Manrope Font** - Primary font configured via CSS variables
- **Dark Mode** - Full dark mode support with `class` strategy
- **shadcn/ui Colors** - Complete color system
- **Tailwind Plugins** - Forms, Typography, Animate

## Important Notes

⚠️ **Content Paths**: Tailwind presets don't inherit content paths. Each app must define its own content array including paths to ui and layouts packages.

## Theme Configuration

The preset includes:
- Font families (Manrope, Inter, Geist)
- Color system (primary, secondary, neutral, sidebar)
- Border radius, shadows, spacing
- Background gradients
- Transition properties
