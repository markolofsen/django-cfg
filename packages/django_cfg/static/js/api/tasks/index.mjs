/**
 * Tasks API Module
 * Re-exports the API client for convenient importing
 * @module tasks
 */

import { TasksAPI, tasksAPI } from './client.mjs';

// Re-export the class and instance
export { TasksAPI, tasksAPI };

// Default export is the instance for convenience
export default tasksAPI;