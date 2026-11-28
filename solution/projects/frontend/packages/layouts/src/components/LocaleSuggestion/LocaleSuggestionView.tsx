'use client';

import { Banner, BannerActions, BannerClose, BannerContent, BannerTitle, Button } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { getLocaleMeta } from '../../layouts/_components/locale-switcher/localeMeta';
import { fill, useLocaleSuggestionCopy } from './i18n';

export interface LocaleSuggestionViewProps {
  /** The visitor's browser language tag: the card is written in it. */
  browserLanguage: string;
  /** The site locale on offer; named in its own language. */
  target: string;
  onSwitch: () => void;
  onDismiss: () => void;
  className?: string;
}

/**
 * The hint card. Fixed, so it never moves the page; a polite status, so it never takes focus; Esc inside it closes it.
 * It speaks the visitor's language (`lang`, `dir`), not the page's.
 */
export function LocaleSuggestionView({ browserLanguage, target, onSwitch, onDismiss, className }: LocaleSuggestionViewProps) {
  const copy = useLocaleSuggestionCopy(browserLanguage);
  const language = getLocaleMeta(target).native;
  const rtl = getLocaleMeta(browserLanguage).rtl === true;

  return (
    <Banner
      lang={browserLanguage}
      dir={rtl ? 'rtl' : 'ltr'}
      data-locale-suggestion=""
      onKeyDown={(event) => {
        if (event.key === 'Escape') onDismiss();
      }}
      onOpenChange={(open) => {
        if (!open) onDismiss();
      }}
      className={cn(
        'fixed inset-x-4 bottom-4 z-50 w-auto flex-col items-stretch gap-3 rounded-lg border shadow-lg',
        'md:inset-x-auto md:end-4 md:w-96',
        className,
      )}
    >
      <BannerContent>
        <BannerTitle className="leading-snug">{fill(copy.title, { language })}</BannerTitle>
      </BannerContent>
      <BannerActions className="justify-between">
        <Button size="sm" onClick={onSwitch}>
          {fill(copy.switch, { language })}
        </Button>
        <BannerClose aria-label={copy.dismiss} title={copy.dismiss} />
      </BannerActions>
    </Banner>
  );
}
