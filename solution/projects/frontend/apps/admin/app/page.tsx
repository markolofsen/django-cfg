import { RedirectPage } from '@djangocfg/layouts/components';
import { redirectToAuth, routes } from '@routes/index';

/**
 * Root page - handles authentication redirect
 * Redirects to /private if authenticated, otherwise to /auth
 */
export default function Page() {
  return (
    <RedirectPage
      authenticatedPath={routes.private.home.path}
      unauthenticatedPath={redirectToAuth()}
    />
  );
}

