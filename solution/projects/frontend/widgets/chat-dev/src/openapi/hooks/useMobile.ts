import { useIsMobile } from '@djangocfg/ui-core/hooks';

export const useMobile = () => {
  const isMobile = useIsMobile();

  return {
    isMobile,
    isDesktop: !isMobile,
  };
}; 