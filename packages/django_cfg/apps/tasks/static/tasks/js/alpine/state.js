/**
 * Dashboard Initial State
 */
export default {
    activeTab: 'overview',
    loading: false,
    autoRefresh: true,
    autoRefreshInterval: null,
    lastUpdateTime: '--:--:--',
    tasks: [],
    queues: [],
    workers: [],
    stats: {},
    filters: {
        status: '',
        queue: '',
        search: ''
    },
    counts: {
        queues: 0,
        workers: 0,
        tasks: 0
    },
    actionMessage: '',
    actionType: 'info',
    showTaskModal: false,
    selectedTask: null,
    pagination: {
        page: 1,
        page_size: 20,
        total_pages: 1,
        total_count: 0,
        has_next: false,
        has_previous: false
    }
};
