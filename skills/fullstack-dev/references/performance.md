# Performance Optimization Guide

## Frontend Performance

### Code Splitting & Lazy Loading

```typescript
// frontend/src/app/page.tsx
import dynamic from 'next/dynamic';
import { lazy, Suspense } from 'react';

// Next.js dynamic import
const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false, // Disable SSR for client-only components
});

// React lazy loading
const AdminPanel = lazy(() => import('@/components/AdminPanel'));

function DashboardPage() {
  return (
    <div>
      <HeavyChart data={chartData} />
      <Suspense fallback={<LoadingSpinner />}>
        <AdminPanel />
      </Suspense>
    </div>
  );
}
```

### Image Optimization

```tsx
// Next.js Image component (automatic optimization)
import Image from 'next/image';

function ProductCard({ product }: { product: Product }) {
  return (
    <Image
      src={product.imageUrl}
      alt={product.name}
      width={300}
      height={200}
      priority={false} // Lazy load by default
      placeholder="blur" // Show blur placeholder
      blurDataURL={product.blurHash} // Low-quality placeholder
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
    />
  );
}

// Responsive images with srcset
<picture>
  <source media="(max-width: 640px)" srcSet="/image-sm.webp" />
  <source media="(max-width: 1024px)" srcSet="/image-md.webp" />
  <img src="/image-lg.webp" alt="Responsive image" loading="lazy" />
</picture>
```

### Bundle Size Optimization

```typescript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // Tree shaking
  experimental: {
    optimizePackageImports: ['lucide-react', '@tanstack/react-query'],
  },
  
  // Webpack config for smaller bundles
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },
});
```

### React Query Optimization

```typescript
// frontend/src/lib/query-client.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000,   // 10 minutes (formerly cacheTime)
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Prefetching
async function prefetchProduct(id: string) {
  await queryClient.prefetchQuery({
    queryKey: ['product', id],
    queryFn: () => fetchProduct(id),
  });
}

// Infinite scroll with pagination
import { useInfiniteQuery } from '@tanstack/react-query';

function useProducts() {
  return useInfiniteQuery({
    queryKey: ['products'],
    queryFn: ({ pageParam = 0 }) => fetchProducts(pageParam),
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: 0,
  });
}
```

### Virtualization for Large Lists

```tsx
// frontend/src/components/VirtualList.tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualProductList({ products }: { products: Product[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: products.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80, // Estimated item height
    overscan: 5, // Render extra items for smooth scrolling
  });
  
  return (
    <div ref={parentRef} className="h-[600px] overflow-auto">
      <div
        style={{ height: `${virtualizer.getTotalSize()}px` }}
        className="relative"
      >
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            <ProductCard product={products[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Backend Performance

### Database Optimization

```python
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Number of connections to keep
    max_overflow=10,       # Additional connections when pool is full
    pool_pre_ping=True,    # Check connection health
    pool_recycle=3600,     # Recycle connections after 1 hour
    echo=False,            # Disable SQL logging in production
)

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### Query Optimization

```python
# backend/app/api/v1/endpoints/products.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

# Eager loading to prevent N+1 queries
async def get_products_with_categories(db: AsyncSession):
    query = select(Product).options(
        selectinload(Product.category),  # Load related data
        joinedload(Product.reviews),     # Join for frequently accessed
    )
    result = await db.execute(query)
    return result.scalars().all()

# Pagination
async def get_products_paginated(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
):
    offset = (page - 1) * page_size
    
    # Get total count
    count_query = select(func.count()).select_from(Product)
    total = await db.scalar(count_query)
    
    # Get paginated results
    query = select(Product).offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }

# Index optimization
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), index=True)  # Single column index
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_product_category_created', 'category_id', 'created_at'),  # Composite index
        Index('ix_product_name_trgm', 'name', postgresql_using='gin'),  # Full-text search
    )
```

### Caching Strategies

```python
# backend/app/core/cache.py
from redis import asyncio as aioredis
import json
from functools import wraps
from typing import Optional
import hashlib

class CacheService:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
    
    async def get(self, key: str) -> Optional[dict]:
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: dict, ttl: int = 300):
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        await self.redis.delete(key)
    
    async def delete_pattern(self, pattern: str):
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

# Decorator for caching
def cached(ttl: int = 300, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{hashlib.md5(str((args, kwargs)).encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=600, key_prefix="products")
async def get_popular_products(db: AsyncSession):
    query = select(Product).order_by(Product.views.desc()).limit(10)
    result = await db.execute(query)
    return result.scalars().all()
```

### Async Background Tasks

```python
# backend/app/tasks/email.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, to: str, subject: str, body: str):
    try:
        # Send email logic
        send_email(to, subject, body)
    except Exception as exc:
        self.retry(exc=exc, countdown=60)  # Retry after 60 seconds

# FastAPI background tasks (for simple tasks)
from fastapi import BackgroundTasks

@app.post("/send-notification")
async def send_notification(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(
        process_notification,
        notification.user_id,
        notification.message,
    )
    return {"status": "queued"}
```

---

## Database Indexing Guide

### Index Types

```sql
-- B-tree index (default, good for equality and range queries)
CREATE INDEX idx_product_price ON products(price);

-- Hash index (faster for equality queries only)
CREATE INDEX idx_product_sku_hash ON products USING hash(sku);

-- GIN index (for full-text search and arrays)
CREATE INDEX idx_product_search ON products USING gin(to_tsvector('english', name || ' ' || description));

-- Partial index (index subset of rows)
CREATE INDEX idx_active_products ON products(category_id) WHERE is_active = true;

-- Covering index (include columns to avoid table lookup)
CREATE INDEX idx_product_covering ON products(category_id) INCLUDE (name, price);
```

### Query Analysis

```sql
-- Analyze query execution plan
EXPLAIN ANALYZE SELECT * FROM products WHERE category_id = 1;

-- Check for sequential scans (bad for large tables)
EXPLAIN ANALYZE SELECT * FROM products WHERE name LIKE '%keyword%';

-- Analyze index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## Caching Patterns

### Cache-Aside Pattern

```python
async def get_product(product_id: int, db: AsyncSession):
    # Try cache first
    cache_key = f"product:{product_id}"
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    # Fetch from database
    product = await db+get(Product, product_id)
    if product:
        # Store in cache
        await cache.set(cache_key, product.dict(), ttl=300)
    return product
```

### Write-Through Pattern

```python
async def update_product(product_id: int, data: ProductUpdate, db: AsyncSession):
    # Update database
    product = await db.get(Product, product_id)
    for key, value in data.dict().items():
        setattr(product, key, value)
    await db.commit()
    
    # Update cache
    cache_key = f"product:{product_id}"
    await cache.set(cache_key, product.dict(), ttl=300)
    
    return product
```

### Cache Invalidation

```python
async def delete_product(product_id: int, db: AsyncSession):
    # Delete from database
    await db.execute(delete(Product).where(Product.id == product_id))
    await db.commit()
    
    # Invalidate cache
    await cache.delete(f"product:{product_id}")
    await cache.delete_pattern("products:*")  # Invalidate list caches
```

---

## Performance Monitoring

### Frontend Metrics

```typescript
// frontend/src/lib/performance.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

export function reportWebVitals() {
  getCLS(console.log);    // Cumulative Layout Shift
  getFID(console.log);    // First Input Delay
  getFCP(console.log);    // First Contentful Paint
  getLCP(console.log);    // Largest Contentful Paint
  getTTFB(console.log);   // Time to First Byte
}

// Send to analytics
function sendToAnalytics(metric: Metric) {
  fetch('/api/analytics', {
    method: 'POST',
    body: JSON.stringify({
      name: metric.name,
      value: metric.value,
      id: metric.id,
    }),
  });
}
```

### Backend Metrics

```python
# backend/app/middleware/metrics.py
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Request
import time

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Latency',
    ['method', 'endpoint']
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

---

## Performance Checklist

### Frontend
- [ ] Code splitting implemented
- [ ] Images optimized (Next.js Image, lazy loading)
- [ ] Bundle size analyzed and minimized
- [ ] React Query caching configured
- [ ] Virtualization for large lists
- [ ] Web Vitals monitored
- [ ] Font optimization (subset, preload)

### Backend
- [ ] Database connection pooling
- [ ] N+1 queries eliminated (eager loading)
- [ ] Proper indexes created
- [ ] Redis caching implemented
- [ ] Background tasks for heavy operations
- [ ] Rate limiting configured
- [ ] Response compression enabled

### Database
- [ ] Indexes on frequently queried columns
- [ ] Composite indexes for multi-column queries
- [ ] Query execution plans analyzed
- [ ] Connection pool sized appropriately
- [ ] Read replicas for read-heavy workloads
