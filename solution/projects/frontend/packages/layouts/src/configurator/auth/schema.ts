/**
 * JSON Schema + uiSchema for an AuthLayout configurator UI.
 *
 * Two independent schemas are exported:
 *   - `authCenteredSchema` / `authCenteredUiSchema` — Apple-style frameless shell
 *   - `authSplitSchema` / `authSplitUiSchema` — two-column card with sidebar
 *
 * Pair with `<JsonSchemaForm density="compact" schema={...} uiSchema={...}>`
 * from `@djangocfg/widget-forms` to get a ready-made sidebar configurator.
 */

import type { CustomJsonSchema7, CustomJsonUiSchema7 } from '@djangocfg/ui-core/lib';

// ─────────────────────────────────────────────────────────────────────────────
// Centered variant
// ─────────────────────────────────────────────────────────────────────────────

export const authCenteredSchema: CustomJsonSchema7 = {
  type: 'object',
  properties: {
    background: {
      type: 'object',
      title: 'Background',
      properties: {
        enabled: {
          type: 'boolean',
          title: 'Enable custom background',
          description: 'When off, uses the default GlowBackground.',
        },
        imageUrl: {
          type: 'string',
          title: 'Image',
          enum: [
            'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=80',
            'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1920&q=80',
            'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=1920&q=80',
            'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=1920&q=80',
            'https://images.unsplash.com/photo-1448375240586-882707db888b?w=1920&q=80',
          ],
          enumNames: ['Mountains', 'Night City', 'Abstract Mesh', 'Ocean Waves', 'Forest Fog'],
          description: 'Full-bleed background image (loaded via useImageLoader).',
        },
        gradient: {
          type: 'string',
          title: 'CSS gradient',
          description: 'Fallback when no image or image fails to load.',
        },
        overlay: {
          type: 'string',
          title: 'Overlay color',
          description: 'e.g. color-mix(in oklab, var(--background) 60%, transparent)',
        },
        blur: {
          type: 'string',
          title: 'Backdrop blur',
          description: 'e.g. 8px, 12px',
        },
      },
    },
    form: {
      type: 'object',
      title: 'Form options',
      properties: {
        showLogo: { type: 'boolean', title: 'Logo on success screen' },
        showTerms: { type: 'boolean', title: 'Terms checkbox' },
        showGithub: { type: 'boolean', title: 'GitHub OAuth button' },
        showGoogle: { type: 'boolean', title: 'Google OAuth button' },
        showSupport: { type: 'boolean', title: 'Support link in footer' },
      },
    },
  },
};

export const authCenteredUiSchema: CustomJsonUiSchema7 = {
  background: {
    'ui:collapsible': true,
    'ui:groups': [
      { title: 'Toggle', fields: ['enabled'], defaultOpen: true },
      { title: 'Style', fields: ['imageUrl', 'gradient', 'overlay', 'blur'], defaultOpen: true },
    ],
    enabled: { 'ui:widget': 'switch' },
    imageUrl: {
      'ui:widget': 'select',
      'ui:disabledWhen': { path: 'background.enabled', eq: false },
    },
    gradient: { 'ui:disabledWhen': { path: 'background.enabled', eq: false } },
    overlay: { 'ui:disabledWhen': { path: 'background.enabled', eq: false } },
    blur: { 'ui:disabledWhen': { path: 'background.enabled', eq: false } },
  },
  form: {
    'ui:collapsible': true,
    showLogo: { 'ui:widget': 'switch' },
    showTerms: { 'ui:widget': 'switch' },
    showGithub: { 'ui:widget': 'switch' },
    showGoogle: { 'ui:widget': 'switch' },
    showSupport: { 'ui:widget': 'switch' },
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Split variant
// ─────────────────────────────────────────────────────────────────────────────

export const authSplitSchema: CustomJsonSchema7 = {
  type: 'object',
  properties: {
    background: {
      type: 'object',
      title: 'Background',
      properties: {
        enabled: {
          type: 'boolean',
          title: 'Enable custom background',
          description: 'When off, uses plain background.',
        },
        imageUrl: {
          type: 'string',
          title: 'Image',
          enum: [
            'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=80',
            'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1920&q=80',
            'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=1920&q=80',
            'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=1920&q=80',
            'https://images.unsplash.com/photo-1448375240586-882707db888b?w=1920&q=80',
          ],
          enumNames: ['Mountains', 'Night City', 'Abstract Mesh', 'Ocean Waves', 'Forest Fog'],
          description: 'Full-bleed background image (loaded via useImageLoader).',
        },
        gradient: {
          type: 'string',
          title: 'CSS gradient',
          description: 'Fallback when no image or image fails to load.',
        },
        overlay: {
          type: 'string',
          title: 'Overlay color',
          description: 'e.g. color-mix(in oklab, var(--background) 60%, transparent)',
        },
        blur: {
          type: 'string',
          title: 'Backdrop blur',
          description: 'e.g. 8px, 12px',
        },
      },
    },
    sidebar: {
      type: 'object',
      title: 'Sidebar',
      properties: {
        enabled: {
          type: 'boolean',
          title: 'Show sidebar',
          description: 'Right column content — visible on desktop only.',
        },
        showQuote: { type: 'boolean', title: 'Show quote' },
        showAuthor: { type: 'boolean', title: 'Show author' },
      },
    },
    form: {
      type: 'object',
      title: 'Form options',
      properties: {
        showLogo: { type: 'boolean', title: 'Logo on success screen' },
        showTerms: { type: 'boolean', title: 'Terms checkbox' },
        showGithub: { type: 'boolean', title: 'GitHub OAuth button' },
        showGoogle: { type: 'boolean', title: 'Google OAuth button' },
        showSupport: { type: 'boolean', title: 'Support link in footer' },
      },
    },
  },
};

export const authSplitUiSchema: CustomJsonUiSchema7 = {
  background: {
    'ui:collapsible': true,
    'ui:groups': [
      { title: 'Toggle', fields: ['enabled'], defaultOpen: true },
      { title: 'Style', fields: ['imageUrl', 'gradient', 'overlay', 'blur'], defaultOpen: true },
    ],
    enabled: { 'ui:widget': 'switch' },
    imageUrl: {
      'ui:widget': 'select',
      'ui:disabledWhen': { path: 'background.enabled', eq: false },
    },
    gradient: { 'ui:disabledWhen': { path: 'background.enabled', eq: false } },
    overlay: { 'ui:disabledWhen': { path: 'background.enabled', eq: false } },
    blur: { 'ui:disabledWhen': { path: 'background.enabled', eq: false } },
  },
  sidebar: {
    'ui:collapsible': true,
    enabled: { 'ui:widget': 'switch' },
    showQuote: {
      'ui:widget': 'switch',
      'ui:disabledWhen': { path: 'sidebar.enabled', eq: false },
    },
    showAuthor: {
      'ui:widget': 'switch',
      'ui:disabledWhen': { path: 'sidebar.enabled', eq: false },
    },
  },
  form: {
    'ui:collapsible': true,
    showLogo: { 'ui:widget': 'switch' },
    showTerms: { 'ui:widget': 'switch' },
    showGithub: { 'ui:widget': 'switch' },
    showGoogle: { 'ui:widget': 'switch' },
    showSupport: { 'ui:widget': 'switch' },
  },
};
