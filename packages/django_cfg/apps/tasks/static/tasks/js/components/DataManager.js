/**
 * Data Manager - Handles data fetching and caching
 */
export class DataManager {
    constructor(api) {
        this.api = api;
        this.cache = new Map();
    }

    async getData(key, fetcher, ttl = 30000) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < ttl) {
            return cached.data;
        }

        const data = await fetcher();
        this.cache.set(key, { data, timestamp: Date.now() });
        return data;
    }

    clearCache() {
        this.cache.clear();
    }
}
