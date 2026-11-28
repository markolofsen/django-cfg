/**
 * API Version Management Utilities
 * Handles version detection, filtering, and URL transformation
 */

import type { ApiEndpoint } from '../types';

export interface ApiVersion {
  id: string;
  name: string;
  description: string;
  isDefault: boolean;
}

// Available API versions
export const API_VERSIONS: ApiVersion[] = [
  {
    id: 'v1',
    name: 'v1',
    description: 'Current stable version',
    isDefault: true,
  },
];

/**
 * Detect version from endpoint path
 */
export const detectEndpointVersion = (path: string): string => {
  // Check for versioned paths like /api/vehicles_api/v1/...
  const versionMatch = path.match(/\/api\/[^/]+\/(v\d+)\//);
  if (versionMatch && versionMatch[1]) {
    return versionMatch[1];
  }
  
  // If no version found, default to v1
  return 'v1';
};

/**
 * Check if endpoint belongs to specific version
 */
export const isEndpointInVersion = (endpoint: ApiEndpoint, version: string): boolean => {
  const endpointVersion = detectEndpointVersion(endpoint.path);
  return endpointVersion === version;
};

/**
 * Filter endpoints by version
 */
export const filterEndpointsByVersion = (endpoints: ApiEndpoint[], version: string): ApiEndpoint[] => {
  return endpoints.filter(endpoint => isEndpointInVersion(endpoint, version));
};

/**
 * Remove duplicate endpoints across versions
 * Keeps only the specified version, removes duplicates from other versions
 */
export const deduplicateEndpoints = (endpoints: ApiEndpoint[], preferredVersion: string): ApiEndpoint[] => {
  const endpointMap = new Map<string, ApiEndpoint>();
  
  // Group endpoints by normalized path (without version)
  const groupedEndpoints = new Map<string, ApiEndpoint[]>();
  
  endpoints.forEach(endpoint => {
    const normalizedPath = normalizeEndpointPath(endpoint.path);
    if (!groupedEndpoints.has(normalizedPath)) {
      groupedEndpoints.set(normalizedPath, []);
    }
    groupedEndpoints.get(normalizedPath)!.push(endpoint);
  });
  
  // For each group, pick the endpoint from preferred version
  groupedEndpoints.forEach((endpointGroup, normalizedPath) => {
    let selectedEndpoint: ApiEndpoint | null = null;
    
    // Try to find endpoint in preferred version
    const versionEndpoint = endpointGroup.find(ep => isEndpointInVersion(ep, preferredVersion));
    if (versionEndpoint) {
      selectedEndpoint = versionEndpoint;
    } else if (endpointGroup.length > 0) {
      // Fallback to first available endpoint
      selectedEndpoint = endpointGroup[0] || null;
    }
    
    if (selectedEndpoint) {
      endpointMap.set(normalizedPath, selectedEndpoint);
    }
  });
  
  return Array.from(endpointMap.values());
};

/**
 * Normalize endpoint path by removing version prefix
 * /api/vehicles_api/v1/vehicles/ -> /api/vehicles_api/vehicles/
 * /api/vehicles_api/vehicles/ -> /api/vehicles_api/vehicles/
 */
export const normalizeEndpointPath = (path: string): string => {
  // Remove version prefix like /v1/, /v2/, etc.
  return path.replace(/\/v\d+\//, '/');
};

/**
 * Convert endpoint path to specific version
 */
export const convertEndpointToVersion = (endpoint: ApiEndpoint, targetVersion: string): ApiEndpoint => {
  const currentVersion = detectEndpointVersion(endpoint.path);
  
  // If already in target version, return as is
  if (currentVersion === targetVersion) {
    return endpoint;
  }
  
  let newPath = endpoint.path;
  
  // Replace version: /api/vehicles_api/v1/vehicles/ -> /api/vehicles_api/v2/vehicles/
  newPath = newPath.replace(/\/v\d+\//, `/${targetVersion}/`);
  
  return {
    ...endpoint,
    path: newPath,
  };
};

/**
 * Get version info by ID
 */
export const getVersionById = (versionId: string): ApiVersion | undefined => {
  return API_VERSIONS.find(v => v.id === versionId);
};

/**
 * Get default version
 */
export const getDefaultVersion = (): ApiVersion => {
  const defaultVersion = API_VERSIONS.find(v => v.isDefault);
  if (defaultVersion) {
    return defaultVersion;
  }
  
  // Fallback to first version if no default is set
  if (API_VERSIONS.length > 0 && API_VERSIONS[0]) {
    return API_VERSIONS[0];
  }
  
  // This should never happen, but TypeScript requires it
  throw new Error('No API versions defined');
};

/**
 * Get version statistics from endpoints
 */
export const getVersionStats = (endpoints: ApiEndpoint[]): Record<string, number> => {
  const stats: Record<string, number> = {};
  
  API_VERSIONS.forEach(version => {
    stats[version.id] = filterEndpointsByVersion(endpoints, version.id).length;
  });
  
  return stats;
};
