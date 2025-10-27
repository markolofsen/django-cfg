/**
 * Centrifugo API Module
 * Re-exports the API client for convenient importing
 * @module centrifugo
 */

import { CentrifugoAPI, centrifugoAPI } from './client.mjs';

// Re-export the class and instance
export { CentrifugoAPI, centrifugoAPI };

// Default export is the instance for convenience
export default centrifugoAPI;