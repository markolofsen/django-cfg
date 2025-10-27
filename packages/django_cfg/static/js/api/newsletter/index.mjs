/**
 * Newsletter API Module
 * Re-exports the API client for convenient importing
 * @module newsletter
 */

import { NewsletterAPI, newsletterAPI } from './client.mjs';

// Re-export the class and instance
export { NewsletterAPI, newsletterAPI };

// Default export is the instance for convenience
export default newsletterAPI;