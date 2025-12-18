# ⚡ Python Performance Guide

## 🎯 Quick Summary
Performance optimization patterns and anti-patterns for Python applications, focusing on memory efficiency, async operations, and scalable code design.

## 📋 Table of Contents
1. [Performance Targets](#performance-targets)
2. [Async Patterns](#async-patterns)
3. [Memory Management](#memory-management)
4. [Database Optimization](#database-optimization)
5. [Profiling & Monitoring](#profiling--monitoring)

## 🔑 Key Principles at a Glance
- **Async first**: Non-blocking I/O for all external operations
- **Batch operations**: Minimize database round trips
- **Memory awareness**: Track allocations and avoid leaks
- **Lazy loading**: Load data only when needed
- **Connection pooling**: Reuse expensive resources

## 🚀 Quick Performance Check
```bash
# Memory profiling
pip install memory-profiler
python -m memory_profiler your_script.py

# Async profiling
pip install aiomonitor
python -m aiomonitor your_async_app.py

# Database query analysis
EXPLAIN ANALYZE your_query;
```

---

## 🎯 Performance Targets

### Response Time Benchmarks
```python
# ✅ REQUIRED - API response times
class PerformanceTargets:
    API_RESPONSE_TIME_MS = 200      # 95th percentile
    DATABASE_QUERY_MS = 50          # Simple queries
    COMPLEX_QUERY_MS = 500          # Complex joins/aggregations
    CACHE_HIT_TIME_MS = 5           # Redis/Memcached
    FILE_OPERATION_MS = 100         # Local file I/O

    # Memory usage per worker/process
    MEMORY_LIMIT_MB = 100           # Base memory footprint
    MEMORY_GROWTH_MB_PER_HOUR = 5   # Acceptable growth rate

    # Throughput requirements
    REQUESTS_PER_SECOND = 100       # Per worker
    CONCURRENT_CONNECTIONS = 1000   # Max simultaneous

    # Error rates
    ERROR_RATE_PERCENT = 1.0        # Maximum acceptable
    TIMEOUT_RATE_PERCENT = 0.5      # Connection timeouts
```

### Monitoring Alerts
```python
# ✅ REQUIRED - Performance monitoring
@dataclass
class PerformanceAlert:
    response_time_95th: float       # Alert if > 500ms
    memory_usage_mb: float          # Alert if > 150MB
    error_rate: float               # Alert if > 2%
    active_connections: int         # Alert if > 800
    queue_depth: int                # Alert if > 100

def check_performance_health() -> PerformanceAlert:
    """Monitor key performance indicators."""
    return PerformanceAlert(
        response_time_95th=get_response_time_percentile(95),
        memory_usage_mb=get_memory_usage(),
        error_rate=get_error_rate(),
        active_connections=get_active_connections(),
        queue_depth=get_queue_depth()
    )
```

---

## 🔄 Async Patterns

### Efficient Async Operations
```python
# ✅ GOOD - Concurrent operations with asyncio.gather
import asyncio
from typing import List
from aiohttp import ClientSession

async def fetch_multiple_cars_efficient(
    car_ids: List[int]
) -> List[CarData]:
    """Fetch multiple cars concurrently."""
    async with ClientSession() as session:
        tasks = [
            fetch_single_car(session, car_id)
            for car_id in car_ids
        ]
        # Concurrent execution
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        cars = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Failed to fetch car: {result}")
                continue
            cars.append(result)

        return cars

async def fetch_single_car(
    session: ClientSession,
    car_id: int
) -> CarData:
    """Fetch single car with timeout and retry."""
    async with session.get(
        f"/api/cars/{car_id}",
        timeout=aiohttp.ClientTimeout(total=5)
    ) as response:
        data = await response.json()
        return CarData.parse_obj(data)

# ❌ BAD - Sequential operations (slow!)
async def fetch_multiple_cars_slow(car_ids: List[int]) -> List[CarData]:
    """Don't do this - sequential fetching is slow!"""
    cars = []
    for car_id in car_ids:  # Sequential - SLOW!
        car = await fetch_single_car_slow(car_id)
        cars.append(car)
    return cars
```

### Database Connection Pooling
```python
# ✅ GOOD - Async connection pool
import asyncpg
from contextlib import asynccontextmanager

class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None

    async def startup(self):
        """Initialize connection pool."""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=5,      # Minimum connections
            max_size=20,     # Maximum connections
            max_queries=50000,  # Rotate connections
            max_inactive_connection_lifetime=300.0,
            command_timeout=60.0
        )

    async def shutdown(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool."""
        async with self.pool.acquire() as connection:
            yield connection

# ✅ GOOD - Batch database operations
async def save_cars_batch(cars: List[CarData]) -> List[int]:
    """Save multiple cars in single transaction."""
    async with db_manager.get_connection() as conn:
        async with conn.transaction():
            # Batch insert - much faster than individual inserts
            query = """
                INSERT INTO cars (brand, model, year, price)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """

            car_tuples = [
                (car.brand, car.model, car.year, car.price)
                for car in cars
            ]

            # Execute batch operation
            result = await conn.executemany(query, car_tuples)
            return [row['id'] for row in result]
```

### Rate Limiting and Backoff
```python
# ✅ GOOD - Intelligent rate limiting
import asyncio
from datetime import datetime, timedelta
from typing import Optional

class RateLimiter:
    def __init__(self, requests_per_second: float = 2.0):
        self.requests_per_second = requests_per_second
        self.last_request: Optional[datetime] = None
        self.request_count = 0
        self.window_start = datetime.utcnow()

    async def acquire(self):
        """Wait if necessary to respect rate limit."""
        now = datetime.utcnow()

        # Reset window if needed
        if now - self.window_start >= timedelta(seconds=1):
            self.request_count = 0
            self.window_start = now

        # Check if we need to wait
        if self.request_count >= self.requests_per_second:
            sleep_time = 1.0 - (now - self.window_start).total_seconds()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                # Reset for new window
                self.request_count = 0
                self.window_start = datetime.utcnow()

        self.request_count += 1
        self.last_request = now

# ✅ GOOD - Exponential backoff for retries
async def fetch_with_retry(
    url: str,
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Optional[dict]:
    """Fetch data with exponential backoff retry."""
    for attempt in range(max_retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limited
                        if attempt < max_retries:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            logger.info(f"Rate limited, retrying in {delay}s")
                            await asyncio.sleep(delay)
                            continue
                    else:
                        response.raise_for_status()

        except asyncio.TimeoutError:
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Timeout, retrying in {delay}s")
                await asyncio.sleep(delay)
                continue
            raise

        except Exception as e:
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Error {e}, retrying in {delay}s")
                await asyncio.sleep(delay)
                continue
            raise

    return None
```

---

## 💾 Memory Management

### Memory-Efficient Data Processing
```python
# ✅ GOOD - Generator for large datasets
def process_cars_memory_efficient(
    car_ids: List[int],
    batch_size: int = 100
) -> Generator[List[CarData], None, None]:
    """Process cars in batches to limit memory usage."""
    for i in range(0, len(car_ids), batch_size):
        batch_ids = car_ids[i:i + batch_size]

        # Process batch
        batch_cars = fetch_cars_batch(batch_ids)
        yield batch_cars

        # Explicit cleanup if needed
        del batch_cars

# ✅ GOOD - Use __slots__ for memory efficiency
class OptimizedCarData:
    """Memory-optimized car data structure."""
    __slots__ = ['id', 'brand', 'model', 'year', 'price']

    def __init__(self, id: int, brand: str, model: str, year: int, price: Decimal):
        self.id = id
        self.brand = brand
        self.model = model
        self.year = year
        self.price = price

# ❌ BAD - Loading all data into memory
def process_all_cars_bad():
    """Don't do this - loads everything into memory!"""
    all_cars = []
    for page in range(1000):  # Could be millions of cars!
        page_cars = fetch_cars_page(page)
        all_cars.extend(page_cars)  # Memory grows without bound!

    return process_cars(all_cars)
```

### Caching Strategies
```python
# ✅ GOOD - LRU cache with size limits
from functools import lru_cache
from typing import Optional
import asyncio

class CacheManager:
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.access_times: Dict[str, datetime] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with LRU eviction."""
        if key in self.cache:
            self.access_times[key] = datetime.utcnow()
            return self.cache[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in cache with TTL."""
        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            await self._evict_lru()

        self.cache[key] = value
        self.access_times[key] = datetime.utcnow()

        # Schedule TTL cleanup
        asyncio.create_task(self._expire_key(key, ttl_seconds))

    async def _evict_lru(self):
        """Remove least recently used item."""
        if not self.access_times:
            return

        lru_key = min(self.access_times.keys(),
                     key=lambda k: self.access_times[k])
        del self.cache[lru_key]
        del self.access_times[lru_key]

    async def _expire_key(self, key: str, ttl_seconds: int):
        """Remove key after TTL expires."""
        await asyncio.sleep(ttl_seconds)
        self.cache.pop(key, None)
        self.access_times.pop(key, None)

# ✅ GOOD - Redis caching for distributed systems
import aioredis
import pickle

class RedisCache:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None

    async def startup(self):
        self.redis = aioredis.from_url(self.redis_url)

    async def get_car_data(self, car_id: int) -> Optional[CarData]:
        """Get car data from cache."""
        cached = await self.redis.get(f"car:{car_id}")
        if cached:
            return CarData.parse_obj(pickle.loads(cached))
        return None

    async def set_car_data(self, car_id: int, car_data: CarData, ttl: int = 3600):
        """Cache car data with TTL."""
        await self.redis.setex(
            f"car:{car_id}",
            ttl,
            pickle.dumps(car_data.dict())
        )
```

---

## 🗄️ Database Optimization

### Query Optimization
```python
# ✅ GOOD - Efficient database queries
class CarRepository:
    async def find_cars_optimized(
        self,
        filters: CarSearchFilters,
        limit: int = 50,
        offset: int = 0
    ) -> List[CarData]:
        """Optimized car search with proper indexing."""

        # Build query with proper indexes
        query = """
            SELECT id, brand, model, year, price, condition
            FROM cars
            WHERE 1=1
        """
        params = []
        param_count = 0

        # Add filters with parameterized queries
        if filters.brand:
            param_count += 1
            query += f" AND brand = ${param_count}"
            params.append(filters.brand)

        if filters.min_price:
            param_count += 1
            query += f" AND price >= ${param_count}"
            params.append(filters.min_price)

        if filters.max_price:
            param_count += 1
            query += f" AND price <= ${param_count}"
            params.append(filters.max_price)

        # Add proper ordering and pagination
        query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
        params.extend([limit, offset])

        # Execute with connection pool
        async with self.db.get_connection() as conn:
            rows = await conn.fetch(query, *params)
            return [CarData.parse_obj(dict(row)) for row in rows]

# ✅ GOOD - Batch operations to reduce round trips
async def update_car_prices_batch(
    price_updates: List[Tuple[int, Decimal]]
) -> int:
    """Update multiple car prices in single transaction."""
    async with db.get_connection() as conn:
        async with conn.transaction():
            # Use UNNEST for bulk updates
            query = """
                UPDATE cars
                SET price = updates.new_price
                FROM (
                    SELECT UNNEST($1::int[]) as car_id,
                           UNNEST($2::decimal[]) as new_price
                ) AS updates
                WHERE cars.id = updates.car_id
            """

            car_ids = [update[0] for update in price_updates]
            new_prices = [update[1] for update in price_updates]

            result = await conn.execute(query, car_ids, new_prices)
            return int(result.split()[-1])  # Return count of updated rows
```

### Database Indexing Strategy
```sql
-- ✅ REQUIRED - Essential indexes for car search
CREATE INDEX CONCURRENTLY idx_cars_brand ON cars(brand);
CREATE INDEX CONCURRENTLY idx_cars_price ON cars(price);
CREATE INDEX CONCURRENTLY idx_cars_year ON cars(year);
CREATE INDEX CONCURRENTLY idx_cars_created_at ON cars(created_at DESC);

-- ✅ GOOD - Composite indexes for common queries
CREATE INDEX CONCURRENTLY idx_cars_brand_price ON cars(brand, price);
CREATE INDEX CONCURRENTLY idx_cars_search ON cars(brand, year, price) WHERE condition = 'available';

-- ✅ GOOD - Partial indexes for frequent filters
CREATE INDEX CONCURRENTLY idx_cars_available ON cars(created_at DESC) WHERE condition = 'available';
CREATE INDEX CONCURRENTLY idx_cars_recent ON cars(brand, price) WHERE created_at > NOW() - INTERVAL '30 days';
```

---

## 📊 Profiling & Monitoring

### Performance Profiling
```python
# ✅ GOOD - Built-in performance monitoring
import time
import asyncio
import functools
import psutil
from contextlib import asynccontextmanager

def profile_performance(func):
    """Decorator to profile function performance."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        start_memory = psutil.Process().memory_info().rss

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            return result
        finally:
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss

            duration_ms = (end_time - start_time) * 1000
            memory_delta_mb = (end_memory - start_memory) / 1024 / 1024

            logger.info(
                f"Performance: {func.__name__} "
                f"took {duration_ms:.2f}ms, "
                f"memory delta: {memory_delta_mb:.2f}MB"
            )

    return wrapper

@asynccontextmanager
async def monitor_operation(operation_name: str):
    """Context manager for monitoring operations."""
    start_time = time.perf_counter()
    start_memory = psutil.Process().memory_info().rss

    try:
        yield
    finally:
        end_time = time.perf_counter()
        end_memory = psutil.Process().memory_info().rss

        duration = end_time - start_time
        memory_delta = (end_memory - start_memory) / 1024 / 1024

        # Send metrics to monitoring system
        await send_metrics({
            'operation': operation_name,
            'duration_seconds': duration,
            'memory_delta_mb': memory_delta,
            'timestamp': time.time()
        })

# Usage example
@profile_performance
async def expensive_car_analysis(car_data: List[CarData]) -> AnalysisResult:
    """Analyze car data with performance monitoring."""
    async with monitor_operation("car_analysis"):
        # Expensive computation here
        return analyze_cars(car_data)
```

### Production Monitoring
```python
# ✅ GOOD - Application metrics
import time
from dataclasses import dataclass
from typing import Dict, List
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUEST_COUNT = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('app_active_connections', 'Active connections')
MEMORY_USAGE = Gauge('app_memory_usage_mb', 'Memory usage in MB')

@dataclass
class PerformanceMetrics:
    requests_per_second: float
    average_response_time_ms: float
    error_rate_percent: float
    active_connections: int
    memory_usage_mb: float

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
        self.request_times: List[float] = []
        self.error_count = 0
        self.total_requests = 0

    def record_request(self, duration_ms: float, is_error: bool = False):
        """Record request metrics."""
        self.request_times.append(duration_ms)
        self.total_requests += 1

        if is_error:
            self.error_count += 1

        # Update Prometheus metrics
        REQUEST_DURATION.observe(duration_ms / 1000)
        if is_error:
            REQUEST_COUNT.labels(method='POST', endpoint='/error').inc()

    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        uptime_seconds = time.time() - self.start_time

        return PerformanceMetrics(
            requests_per_second=self.total_requests / uptime_seconds,
            average_response_time_ms=sum(self.request_times) / len(self.request_times) if self.request_times else 0,
            error_rate_percent=(self.error_count / self.total_requests * 100) if self.total_requests > 0 else 0,
            active_connections=get_active_connections(),
            memory_usage_mb=psutil.Process().memory_info().rss / 1024 / 1024
        )
```

---

## ✅ Performance Checklist

### Code Review Performance Check
- [ ] All I/O operations are async
- [ ] Database queries use connection pooling
- [ ] Batch operations used for multiple DB calls
- [ ] Memory usage monitored for large datasets
- [ ] Caching implemented for expensive operations
- [ ] Rate limiting in place for external APIs
- [ ] Error handling includes exponential backoff

### Production Deployment Check
- [ ] Performance monitoring configured
- [ ] Database indexes optimized for queries
- [ ] Connection pool sizes tuned for load
- [ ] Memory limits set for containers
- [ ] Load testing completed with realistic data
- [ ] Performance regression tests in CI/CD

**Remember**: Performance optimization should be data-driven. Profile first, optimize second, and always measure the impact of changes!
