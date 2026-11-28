import { Fragment, type ReactNode } from 'react';

import { cn } from '../../../lib';
import {
  DropdownMenuCheckboxItem,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
} from '../dropdown-menu';
import { MenuIndicatorRow, MenuRow } from './menu-row';
import type { MenuItem } from './types';

interface RenderOptions {
  showDescriptions: boolean;
  /** Applied to every submenu panel at any depth; a `MenuSubmenuItem` may
   *  override it per-branch with its own `contentClassName`. */
  submenuClassName?: string;
}

/** Drop `hidden` rows before rendering. */
function isVisible(item: MenuItem): boolean {
  return !('hidden' in item && item.hidden);
}

/**
 * Recursive renderer — powers both the root content and every
 * `SubContent`. Pure: it only maps data to Radix elements.
 */
export function renderItems(
  items: MenuItem[],
  opts: RenderOptions,
): ReactNode {
  return items.filter(isVisible).map((item, index) => {
    switch (item.kind) {
      case 'separator':
        return <DropdownMenuSeparator key={item.id ?? `sep-${index}`} />;

      case 'label':
        return (
          <DropdownMenuLabel key={item.id ?? `label-${index}`} className="font-normal text-muted-foreground">
            {item.label}
          </DropdownMenuLabel>
        );

      case 'custom':
        return <Fragment key={item.id}>{item.render()}</Fragment>;

      case 'item':
        return (
          <DropdownMenuItem
            key={item.id}
            href={item.href}
            variant={item.variant}
            disabled={item.disabled}
            onSelect={(event) => {
              // closeOnSelect=false → keep the menu open.
              if (item.closeOnSelect === false) event.preventDefault();
              item.onSelect?.(event);
            }}
          >
            <MenuRow
              icon={item.icon}
              label={item.label}
              description={item.description}
              shortcut={item.shortcut}
              showDescription={opts.showDescriptions}
            />
          </DropdownMenuItem>
        );

      case 'submenu':
        return (
          <DropdownMenuSub key={item.id}>
            <DropdownMenuSubTrigger disabled={item.disabled}>
              <MenuRow
                icon={item.icon}
                label={item.label}
                description={item.description}
                showDescription={opts.showDescriptions}
              />
            </DropdownMenuSubTrigger>
            <DropdownMenuPortal>
              {/* Per-branch class wins over the builder-wide one. Height +
                  scroll come from the primitive — see DropdownMenuSubContent. */}
              <DropdownMenuSubContent
                className={cn(opts.submenuClassName, item.contentClassName)}
              >
                {renderItems(item.items, opts)}
              </DropdownMenuSubContent>
            </DropdownMenuPortal>
          </DropdownMenuSub>
        );

      case 'checkbox':
        return (
          <DropdownMenuCheckboxItem
            key={item.id}
            checked={item.checked}
            disabled={item.disabled}
            onCheckedChange={item.onCheckedChange}
          >
            <MenuIndicatorRow
              icon={item.icon}
              label={item.label}
              description={item.description}
              shortcut={item.shortcut}
              showDescription={opts.showDescriptions}
            />
          </DropdownMenuCheckboxItem>
        );

      case 'radio-group':
        return (
          <Fragment key={item.id}>
            {item.label ? (
              <DropdownMenuLabel>{item.label}</DropdownMenuLabel>
            ) : null}
            <DropdownMenuRadioGroup
              value={item.value}
              onValueChange={item.onValueChange}
            >
              {item.options.filter((o) => !o.hidden).map((option) => (
                <DropdownMenuRadioItem
                  key={option.id}
                  value={option.value}
                  disabled={option.disabled}
                  onSelect={(event) => {
                    // closeOnSelect=false → keep the menu open so the selection
                    // can reveal more of the same menu (e.g. an engine preview).
                    if (item.closeOnSelect === false) event.preventDefault();
                  }}
                >
                  <MenuIndicatorRow
                    icon={option.icon}
                    label={option.label}
                    description={option.description}
                    shortcut={option.shortcut}
                    showDescription={opts.showDescriptions}
                  />
                </DropdownMenuRadioItem>
              ))}
            </DropdownMenuRadioGroup>
          </Fragment>
        );

      case 'section': {
        // A separator follows the section unless explicitly disabled or
        // it is the last visible item.
        const isLast =
          index === items.filter(isVisible).length - 1;
        const withSeparator = item.separator !== false && !isLast;
        return (
          <Fragment key={item.id}>
            <DropdownMenuGroup>
              {item.label ? (
                <DropdownMenuLabel>{item.label}</DropdownMenuLabel>
              ) : null}
              {renderItems(item.items, opts)}
            </DropdownMenuGroup>
            {withSeparator ? <DropdownMenuSeparator /> : null}
          </Fragment>
        );
      }

      default: {
        // Exhaustiveness guard — a new `kind` without a branch fails here.
        const _never: never = item;
        return _never;
      }
    }
  });
}
