import type { StoryContext } from '@storybook/nextjs-vite';

export interface DjangoCfgStoryParameters {
  /** Reset browser storage around the story unless persistence is the subject. */
  storage?: 'reset' | 'preserve';
}

type ContextWithDjangoCfg = StoryContext & {
  parameters: StoryContext['parameters'] & {
    djangocfg?: DjangoCfgStoryParameters;
  };
};

/**
 * Isolate browser state that otherwise survives navigation between stories.
 *
 * Persistent-state demonstrations opt out explicitly. The reset happens both
 * before and after a story so a normal story cannot contaminate a later test.
 */
export function storyLifecycle(context: StoryContext) {
  const parameters = (context as ContextWithDjangoCfg).parameters.djangocfg;
  const shouldResetStorage = parameters?.storage !== 'preserve';
  const bodyStyle = document.body.getAttribute('style');

  if (shouldResetStorage) {
    window.localStorage.clear();
    window.sessionStorage.clear();
  }

  return () => {
    if (bodyStyle === null) document.body.removeAttribute('style');
    else document.body.setAttribute('style', bodyStyle);

    if (shouldResetStorage) {
      window.localStorage.clear();
      window.sessionStorage.clear();
    }
  };
}
