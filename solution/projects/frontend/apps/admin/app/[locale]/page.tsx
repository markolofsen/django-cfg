import { RedirectPage } from '@djangocfg/layouts/components';
import { redirectToAuth, routes } from '@routes/index';

import {
    AIDocsSection, CTASectionComponent, FeaturesSection, HeroSection, QuickStartSection
} from '../_components/landing';

export default function Page() {
  const useRedirect = false

  if (useRedirect) {
    /* Redirect to /private if authenticated, otherwise to /auth */
    return (
      <RedirectPage
        authenticatedPath={routes.private.home.path}
        unauthenticatedPath={redirectToAuth()}
      />
    )
  }

  return (
    <main>
      <HeroSection />
      <QuickStartSection />
      <AIDocsSection />
      <FeaturesSection />
      <CTASectionComponent />
    </main>
  )
}
