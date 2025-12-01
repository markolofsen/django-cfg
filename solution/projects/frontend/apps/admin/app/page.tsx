import { HomePage } from '@djangocfg/nextjs/components';
import { redirectToAuth, routes } from '@routes/index';

/**
 * Root page - handles authentication redirect
 * Redirects to /private if authenticated, otherwise to /auth
 */
export default function Page() {
  return (
    <HomePage
      authenticatedPath={routes.user.home.path}
      unauthenticatedPath={redirectToAuth()}
    />
  );
}

