#!/bin/bash

# Unified Task Testing Configuration
# Shared configuration for all django-cfg task tests

# --- Paths ---
# Get the directory of this shared.sh file
SHARED_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
export DJANGO_PROJECT_DIR="$(cd "$SHARED_SCRIPT_DIR/../../.." && pwd)"
export TEST_TASKS_DIR="$DJANGO_PROJECT_DIR/scripts/test_tasks"

# --- Redis Configuration ---
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
export REDIS_DB="2"  # As configured in TaskConfig auto-initialization

# --- Dramatiq Configuration ---
export WORKER_PROCESSES="2"
export WORKER_THREADS="2"
export DRAMATIQ_TIMEOUT="60"  # seconds

# --- Test Configuration ---
export TEST_TIMEOUT="60"  # seconds
export CLEANUP_ON_EXIT="true"

# --- File Paths ---
export BASE_LOG_DIR="/tmp/django_cfg_tasks"
export BASE_PID_DIR="/tmp/django_cfg_tasks"

# Create directories if they don't exist
mkdir -p "$BASE_LOG_DIR" "$BASE_PID_DIR"

# --- Colors ---
export COLOR_INFO="\033[0;34m"
export COLOR_SUCCESS="\033[0;32m"
export COLOR_ERROR="\033[0;31m"
export COLOR_WARNING="\033[0;33m"
export COLOR_RESET="\033[0m"

# --- Logging Functions ---
log_info() {
    echo -e "${COLOR_INFO}🚀 $1${COLOR_RESET}"
}

log_success() {
    echo -e "${COLOR_SUCCESS}✅ $1${COLOR_RESET}"
}

log_error() {
    echo -e "${COLOR_ERROR}❌ $1${COLOR_RESET}"
}

log_warning() {
    echo -e "${COLOR_WARNING}⚠️  $1${COLOR_RESET}"
}

# --- Queue-specific functions ---
get_queue_log_file() {
    local queue_name="$1"
    echo "$BASE_LOG_DIR/${queue_name}_worker.log"
}

get_queue_pid_file() {
    local queue_name="$1"
    echo "$BASE_PID_DIR/${queue_name}_worker.pid"
}

# --- Worker Management Functions ---
check_django_environment() {
    log_info "Checking Django environment..."
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Check if manage.py exists
    if [ ! -f "manage.py" ]; then
        log_error "manage.py not found in $DJANGO_PROJECT_DIR"
        return 1
    fi
    
    # Check if poetry is available
    if ! command -v poetry &> /dev/null; then
        log_error "Poetry not found in PATH"
        return 1
    fi
    
    # Test Django settings
    log_info "Testing Django settings..."
    if ! poetry run python manage.py check --deploy 2>/dev/null; then
        log_warning "Django check failed, but continuing..."
    fi
    
    # Test rundramatiq command availability
    log_info "Testing rundramatiq command..."
    if ! poetry run python manage.py help rundramatiq &>/dev/null; then
        log_error "rundramatiq command not available"
        return 1
    fi
    
    log_success "Django environment check passed"
    return 0
}

start_worker() {
    local queue_name="$1"
    local log_file=$(get_queue_log_file "$queue_name")
    local pid_file=$(get_queue_pid_file "$queue_name")
    
    log_info "Starting $queue_name worker..."
    log_info "Queue: $queue_name"
    log_info "Processes: $WORKER_PROCESSES"
    log_info "Threads: $WORKER_THREADS"
    log_info "Log file: $log_file"
    log_info "PID file: $pid_file"
    
    # Create directories for logs and PID files
    mkdir -p "$(dirname "$log_file")"
    mkdir -p "$(dirname "$pid_file")"
    
    # Check Django environment first
    if ! check_django_environment; then
        log_error "Django environment check failed"
        return 1
    fi
    
    cd "$DJANGO_PROJECT_DIR"
    
    # Start dramatiq worker
    log_info "Executing command: poetry run python manage.py rundramatiq --processes $WORKER_PROCESSES --threads $WORKER_THREADS --queues $queue_name"
    
    poetry run python manage.py rundramatiq \
        --processes "$WORKER_PROCESSES" \
        --threads "$WORKER_THREADS" \
        --queues "$queue_name" \
        > "$log_file" 2>&1 &
    
    local worker_pid=$!
    echo "$worker_pid" > "$pid_file"
    
    log_info "Worker started with PID: $worker_pid"
    
    # Wait a moment for worker to start
    sleep 3
    
    # Check if worker is still running
    if kill -0 "$worker_pid" 2>/dev/null; then
        log_success "$queue_name worker started successfully with PID: $worker_pid"
        log_info "Monitor logs: tail -f $log_file"
        return 0
    else
        log_error "Failed to start $queue_name worker - process died"
        log_error "Last 20 lines from log file:"
        if [ -f "$log_file" ]; then
            tail -20 "$log_file" | while IFS= read -r line; do
                log_error "  $line"
            done
        else
            log_error "  Log file not found: $log_file"
        fi
        return 1
    fi
}

stop_worker() {
    local queue_name="$1"
    local pid_file=$(get_queue_pid_file "$queue_name")
    
    if [ -f "$pid_file" ]; then
        local worker_pid=$(cat "$pid_file")
        if kill -0 "$worker_pid" 2>/dev/null; then
            log_info "Stopping $queue_name worker (PID: $worker_pid)..."
            kill "$worker_pid"
            
            # Wait for graceful shutdown
            local count=0
            while kill -0 "$worker_pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 "$worker_pid" 2>/dev/null; then
                log_warning "Force killing $queue_name worker..."
                kill -9 "$worker_pid"
            fi
            
            log_success "$queue_name worker stopped"
        else
            log_warning "$queue_name worker was not running"
        fi
        rm -f "$pid_file"
    else
        log_warning "No PID file found for $queue_name worker"
    fi
}

# --- Cleanup function ---
cleanup_all() {
    log_info "Cleaning up all workers..."
    
    # Stop all workers
    for queue in knowbase payments; do
        stop_worker "$queue"
    done
    
    # Clean up temp files
    rm -rf "$BASE_LOG_DIR" "$BASE_PID_DIR"
    
    log_success "Cleanup completed"
}

# --- Trap for cleanup on exit ---
if [ "$CLEANUP_ON_EXIT" = "true" ]; then
    trap cleanup_all EXIT INT TERM
fi

# --- Test Validation Functions ---
validate_environment() {
    log_info "Validating test environment..."
    
    # Check if we're in the right directory
    if [ ! -f "$DJANGO_PROJECT_DIR/manage.py" ]; then
        log_error "manage.py not found in $DJANGO_PROJECT_DIR"
        return 1
    fi
    
    # Check if poetry is available
    if ! command -v poetry >/dev/null 2>&1; then
        log_error "Poetry not found. Please install poetry."
        return 1
    fi
    
    # Check if Redis is running
    if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping >/dev/null 2>&1; then
        log_error "Redis is not running on $REDIS_HOST:$REDIS_PORT"
        return 1
    fi
    
    log_success "Environment validation passed"
    return 0
}

# --- Task Testing Functions ---
wait_for_task_completion() {
    local task_id="$1"
    local timeout="$2"
    local queue_name="$3"
    
    log_info "Waiting for task $task_id to complete (timeout: ${timeout}s)..."
    
    local count=0
    while [ $count -lt $timeout ]; do
        # Check task status in logs
        local log_file=$(get_queue_log_file "$queue_name")
        if grep -q "✅.*$task_id" "$log_file" 2>/dev/null; then
            log_success "Task $task_id completed successfully"
            return 0
        elif grep -q "❌.*$task_id" "$log_file" 2>/dev/null; then
            log_error "Task $task_id failed"
            return 1
        fi
        
        sleep 1
        count=$((count + 1))
    done
    
    log_error "Task $task_id timed out after ${timeout}s"
    return 1
}

# Export all functions
export -f log_info log_success log_error log_warning
export -f get_queue_log_file get_queue_pid_file
export -f start_worker stop_worker cleanup_all
export -f validate_environment wait_for_task_completion
