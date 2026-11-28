/**
 * JSON Schema + uiSchema for a `PrivateLayout` configurator UI.
 *
 * The shape mirrors the real `PrivateLayout` runtime API:
 *   - `shell.*`     → `visual` prop (`LayoutVisualConfig`)
 *   - `sidebar.*`   → flags consumed by `SidebarConfig` (caller still maps these
 *                     into a real `SidebarConfig` with concrete `groups`)
 *   - `header.*`    → fields consumed by `HeaderConfig`
 *
 * Pair with `<JsonSchemaForm density="compact" schema={...} uiSchema={...}>`
 * from `@djangocfg/widget-forms` to get a ready-made sidebar configurator. The
 * `defaultPrivateLayoutConfiguratorData` is a safe initial value that already
 * matches the schema (no nullable fields, no missing keys).
 *
 * Playground-only knobs (sample item count, banner toggles, etc.) live in the
 * consuming app, not here — this stays a clean view of the real layout API.
 */

import type { CustomJsonSchema7, CustomJsonUiSchema7 } from '@djangocfg/ui-core/lib';

/** Strongly-typed mirror of the schema — feed this back into PrivateLayout. */
export interface PrivateLayoutConfiguratorData {
  shell: {
    variant: 'full-bleed' | 'boxed';
    inset: number;
    radius: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl';
    background: 'sidebar' | 'muted' | 'card' | 'background';
    border: boolean;
    maxWidth: 'none' | '7xl' | 'screen-xl' | 'screen-2xl';
  };
  sidebar: {
    activeIndicator: 'background' | 'rail' | 'both';
    groupLabelStyle: 'uppercase' | 'plain';
    collapsibleGroups: boolean;
    showFeatured: boolean;
  };
  header: {
    userPlan: string;
    showSecondaryAction: boolean;
    accountAction: 'menu' | 'dialog';
    showSwitcher: boolean;
  };
}

export const privateLayoutConfiguratorSchema: CustomJsonSchema7 = {
  type: 'object',
  properties: {
    shell: {
      type: 'object',
      title: 'Shell',
      properties: {
        variant: {
          type: 'string',
          title: 'Variant',
          enum: ['full-bleed', 'boxed'],
          description: '`boxed` paints a sidebar-coloured canvas around a rounded content card.',
        },
        inset: {
          type: 'integer',
          title: 'Inset (md+)',
          minimum: 0,
          maximum: 32,
          description: 'Gap between the card and viewport edges.',
        },
        radius: {
          type: 'string',
          title: 'Radius',
          enum: ['sm', 'md', 'lg', 'xl', '2xl', '3xl'],
        },
        background: {
          type: 'string',
          title: 'Canvas background',
          enum: ['sidebar', 'muted', 'card', 'background'],
          description: 'Colour painted behind the boxed card.',
        },
        border: {
          type: 'boolean',
          title: 'Border on card',
          description: '1px hairline border around the boxed card.',
        },
        maxWidth: {
          type: 'string',
          title: 'Inner max-width',
          enum: ['none', '7xl', 'screen-xl', 'screen-2xl'],
        },
      },
    },
    sidebar: {
      type: 'object',
      title: 'Sidebar',
      properties: {
        activeIndicator: {
          type: 'string',
          title: 'Active indicator',
          enum: ['background', 'rail', 'both'],
          description: 'Visual treatment for the active nav item.',
        },
        groupLabelStyle: {
          type: 'string',
          title: 'Group label style',
          enum: ['uppercase', 'plain'],
          description: 'Collapsible groups always render `plain` regardless of this setting.',
        },
        collapsibleGroups: {
          type: 'boolean',
          title: 'Collapsible groups',
          description: 'Mailersend-style accordion: label becomes a clickable trigger.',
        },
        showFeatured: {
          type: 'boolean',
          title: 'Featured CTA tile',
          description: 'Accent-tinted tile rendered below groups.',
        },
      },
    },
    header: {
      type: 'object',
      title: 'Header / account footer',
      properties: {
        userPlan: {
          type: 'string',
          title: 'User plan',
          enum: ['', 'Free plan', 'Pro plan', 'Max plan', 'Enterprise'],
          description: 'Subtitle under the display name in the footer trigger. Empty hides it.',
        },
        showSecondaryAction: {
          type: 'boolean',
          title: 'Footer secondary action',
          description: 'Adds a download-style icon button inside the footer trigger with a pulsing accent dot.',
        },
        accountAction: {
          type: 'string',
          title: 'Account action',
          enum: ['menu', 'dialog'],
          description: "'menu' opens a dropdown; 'dialog' opens the global ProfileDialog.",
        },
        showSwitcher: {
          type: 'boolean',
          title: 'Brand switcher',
          description: 'Replace the static brand with a workspace/account dropdown.',
        },
      },
    },
  },
};

export const privateLayoutConfiguratorUiSchema: CustomJsonUiSchema7 = {
  shell: {
    'ui:collapsible': true,
    inset: {
      'ui:widget': 'slider',
      'ui:options': { unit: 'px', step: 2, showInput: false },
      'ui:disabledWhen': { path: 'shell.variant', notEq: 'boxed' },
    },
    radius: {
      'ui:disabledWhen': { path: 'shell.variant', notEq: 'boxed' },
    },
    background: {
      'ui:disabledWhen': { path: 'shell.variant', notEq: 'boxed' },
    },
    border: {
      'ui:widget': 'switch',
      'ui:disabledWhen': { path: 'shell.variant', notEq: 'boxed' },
    },
  },
  sidebar: {
    'ui:collapsible': true,
    'ui:groups': [
      {
        title: 'Visual',
        fields: ['activeIndicator', 'groupLabelStyle', 'collapsibleGroups', 'showFeatured'],
        defaultOpen: true,
      },
    ],
    collapsibleGroups: { 'ui:widget': 'switch' },
    showFeatured: { 'ui:widget': 'switch' },
  },
  header: {
    'ui:collapsible': true,
    showSecondaryAction: { 'ui:widget': 'switch' },
    showSwitcher: { 'ui:widget': 'switch' },
    accountAction: {
      'ui:widget': 'radio',
      'ui:options': { inline: true },
    },
  },
};

export const defaultPrivateLayoutConfiguratorData: PrivateLayoutConfiguratorData = {
  shell: {
    variant: 'boxed',
    inset: 12,
    radius: '2xl',
    background: 'sidebar',
    border: true,
    maxWidth: 'none',
  },
  sidebar: {
    activeIndicator: 'background',
    groupLabelStyle: 'uppercase',
    collapsibleGroups: false,
    showFeatured: false,
  },
  header: {
    userPlan: 'Pro plan',
    showSecondaryAction: false,
    accountAction: 'menu',
    showSwitcher: false,
  },
};
