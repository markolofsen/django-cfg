import { useEffect, useState } from 'react';
import {
  DocsContainer,
  type DocsContainerProps,
} from '@storybook/addon-docs/blocks';
import { themes } from 'storybook/theming';

/** Keep the standalone Docs document synchronized with the canvas theme. */
export function ThemedDocsContainer({
  context,
  children,
}: React.PropsWithChildren<DocsContainerProps>) {
  const readTheme = (): string => {
    try {
      const docsContext = context as {
        primaryStory?: unknown;
        getStoryContext?: (story: unknown) => {
          globals?: Record<string, string>;
        };
      };

      if (docsContext.primaryStory && docsContext.getStoryContext) {
        return (
          docsContext.getStoryContext(docsContext.primaryStory).globals?.theme ??
          'dark'
        );
      }

      return 'dark';
    } catch {
      return 'dark';
    }
  };

  const [theme, setTheme] = useState(readTheme);

  useEffect(() => {
    const onGlobalsUpdated = () => setTheme(readTheme());
    context.channel.on('globalsUpdated', onGlobalsUpdated);
    return () => context.channel.off('globalsUpdated', onGlobalsUpdated);
  }, [context]);

  return (
    <DocsContainer
      context={context}
      theme={theme === 'light' ? themes.light : themes.dark}
    >
      {children}
    </DocsContainer>
  );
}
