/**
 * Contact Form API Route
 * 
 * Uses ready-to-use route handler from @djangocfg/nextjs/contact.
 * apiUrl is passed from ContactFormProvider in request body.
 * 
 * Note: For static export builds, this route is marked as static to allow the build to complete.
 */

import { createContactRoute } from '@djangocfg/nextjs/contact';

// Mark as static for static export compatibility
export const dynamic = 'force-static';
export const revalidate = false;

// Create and export POST handler
// apiUrl will be taken from request body (_apiUrl field) or fallback to env
export const POST = createContactRoute();

