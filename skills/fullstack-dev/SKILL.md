---
name: fullstack-dev
description: Create and develop full-stack web applications with modern frontend and Python backend. Use this skill when the user wants to build a web application, create a new project, set up frontend and backend, design APIs, implement authentication, or work on any full-stack development task. Trigger on phrases like "create an app", "build a web application", "full-stack project", "set up frontend and backend", "develop a web app", or when the user describes a web application idea.
---

# Full-Stack Development Skill

A comprehensive skill for building beautiful, production-ready full-stack web applications.

## Technology Stack Overview

### Frontend Technologies

**Core Framework:**
- React 18+ with TypeScript
- Next.js 14+ (App Router) for SSR/SSG
- Vite for SPA projects

**State Management:**
- Zustand (lightweight global state)
- TanStack Query (server state)
- React Context (simple cases)

**Styling & UI:**
- TailwindCSS (utility-first)
- shadcn/ui (beautiful components)
- Framer Motion (animations)
- Lucide Icons
- Radix UI (accessible primitives)

**Forms & Validation:**
- React Hook Form
- Zod (schema validation)

**Data Fetching:**
- Axios / Fetch API
- TanStack Query

**Testing:**
- Vitest
- React Testing Library
- Playwright (E2E)

### Backend Technologies (Python)

**Web Frameworks:**
- FastAPI (async, modern, recommended)
- Django (batteries-included, ORM, admin)
- Flask (lightweight, flexible)
- Starlette (async minimal)

**ORM & Database:**
- SQLAlchemy (SQL ORM)
- Django ORM
- Tortoise ORM (async)
- Alembic (migrations)
- Pydantic (validation)

**Authentication:**
- JWT (python-jose, PyJWT)
- OAuth2 (authlib)
- Passlib (password hashing)

**Task Queue:**
- Celery (distributed tasks)
- Dramatiq (alternative to Celery)
- ARQ (async task queue)

**API & Documentation:**
- OpenAPI/Swagger (auto-generated)
- GraphQL (strawberry, ariadne)

**Testing:**
- pytest
- pytest-asyncio
- httpx (async HTTP client)

### DevOps & Infrastructure

**Containerization:**
- Docker
- Docker Compose
- Multi-stage builds

**CI/CD:**
- GitHub Actions
- GitLab CI
- Docker Hub

**Cloud Platforms:**
- Vercel (frontend)
- Railway / Render (backend)
- AWS / GCP / Azure

---

## Design Principles

### Visual Aesthetics

**Color Systems:**
- Use CSS custom properties for theming
- Support light/dark mode by default
- Follow 60-30-10 rule (primary, secondary, accent)
- Use semantic colors (success, warning, error, info)

**Typography:**
- System font stack for performance
- Clear hierarchy (H1 → H6, body, small)
- Optimal line height (1.5-1.7 for body)
- Responsive font sizes

**Spacing & Layout:**
- Consistent spacing scale (4px base)
- Responsive breakpoints (sm, md, lg, xl, 2xl)
- Grid system for complex layouts
- Adequate white space

**Components:**
- Consistent border radius
- Subtle shadows for depth
- Smooth transitions (150-300ms)
- Clear visual hierarchy

### UX Best Practices

**Feedback:**
- Loading states (skeletons, spinners)
- Error messages (clear, actionable)
- Success confirmations
- Optimistic updates

**Accessibility:**
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus management
- Color contrast (WCAG 2.1)

**Performance:**
- Lazy loading
- Code splitting
- Image optimization
- Caching strategies

---

## Project Structure

### Full-Stack Project

```
project-name/
├── frontend/                    # React/Next.js application
│   ├── src/
│   │   ├── app/                 # Next.js app router pages
│   │   ├── components/
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── forms/           # Form components
│   │   │   ├── layouts/         # Layout components
│   │   │   └── features/        # Feature-specific components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utilities, API client
│   │   ├── stores/              # Zustand stores
│   │   ├── types/               # TypeScript types
│   │   └── styles/              # Global styles
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── Dockerfile
│
├── backend/                     # Python application
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   └── router.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tasks/               # Celery tasks
│   │   └── main.py
│   ├── tests/
│   ├── alembic/
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── Dockerfile
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── .github/
│   └── workflows/
│       └── ci.yml
└── README.md
```

---

## Workflow

### Phase 1: Requirements & Design

1. **Understand requirements:**
   - Application purpose and target users
   - Core features and user stories
   - Technical constraints

2. **Design decisions:**
   - Choose framework (FastAPI vs Django vs Flask)
   - Database choice (PostgreSQL, MySQL, MongoDB)
   - Authentication method
   - Deployment target

3. **UI/UX planning:**
   - Page structure and navigation
   - Component hierarchy
   - Color palette and typography
   - Responsive breakpoints

### Phase 2: Backend Development

1. **Project setup:**
   ```bash
   # FastAPI
   pip install fastapi uvicorn sqlalchemy alembic pydantic python-jose passlib

   # Django
   pip install django djangorestframework django-cors-headers

   # Flask
   pip install flask flask-sqlalchemy flask-migrate flask-jwt-extended
   ```

2. **Core configuration:**
   - Environment variables (pydantic-settings)
   - Database connection
   - CORS settings
   - Logging

3. **Models & schemas:**
   - SQLAlchemy / Django models
   - Pydantic schemas for validation
   - Relationships and indexes

4. **API endpoints:**
   - RESTful CRUD operations
   - Authentication routes
   - Input validation
   - Error handling

5. **Background tasks (if needed):**
   - Celery configuration
   - Task definitions
   - Result backend

### Phase 3: Frontend Development

1. **Project setup:**
   ```bash
   # Next.js
   npx create-next-app@latest frontend --typescript --tailwind --app

   # Vite + React
   npm create vite@latest frontend -- --template react-ts
   ```

2. **Install dependencies:**
   ```bash
   npm install @tanstack/react-query zustand axios react-hook-form zod
   npm install framer-motion lucide-react
   npx shadcn-ui@latest init
   ```

3. **Setup theming:**
   - Configure TailwindCSS
   - Setup shadcn/ui
   - Define color palette
   - Create dark mode toggle

4. **Build components:**
   - Layout components (Header, Sidebar, Footer)
   - UI components (Button, Input, Card, Modal)
   - Form components with validation
   - Feature components

5. **Connect to backend:**
   - API client setup
   - React Query hooks
   - Authentication flow

### Phase 4: Docker & Deployment

1. **Create Dockerfiles:**
   - Multi-stage builds for optimization
   - Production vs development configs

2. **Docker Compose:**
   - Service orchestration
   - Volume management
   - Network configuration

3. **CI/CD pipeline:**
   - Automated testing
   - Build and push images
   - Deployment automation

---

## Code Templates

### Backend: FastAPI with Modern Structure

**`app/core/config.py`:**
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "My App"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**`app/main.py`:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to database, init services
    yield
    # Shutdown: cleanup

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Backend: Django Configuration

**`settings.py` (key parts):**
```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    # Local apps
    'myapp',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Frontend: Next.js App Structure

**`src/app/layout.tsx`:**
```tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'My App',
  description: 'A beautiful full-stack application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

**`src/app/providers.tsx`:**
```tsx
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from 'next-themes'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system">
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  )
}
```

**`src/lib/api.ts`:**
```typescript
import axios from 'axios'

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### Frontend: Beautiful Component Example

**`src/components/ui/button.tsx`:**
```tsx
import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = 'Button'
```

### Docker Configuration

**`backend/Dockerfile`:**
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY ./app ./app

RUN adduser --disabled-password --gecos '' appuser
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`frontend/Dockerfile`:**
```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000/api/v1

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## Framework Selection Guide

### When to use FastAPI:
- Need async/await support
- Building APIs (not full websites)
- Want automatic OpenAPI docs
- Modern Python (3.10+)
- High performance requirements

### When to use Django:
- Need admin panel
- ORM with complex relationships
- Batteries-included approach
- Traditional web app with templates
- Rapid development

### When to use Flask:
- Microservices
- Simple APIs
- Maximum flexibility
- Learning projects
- Custom architecture

---

## Reference Files

For detailed information, see:
- `references/api-design.md` - RESTful API patterns
- `references/database.md` - Database patterns and migrations
- `references/deployment.md` - Docker and cloud deployment
- `references/design-system.md` - UI/UX design patterns
- `references/security.md` - Security best practices (XSS, CSRF, JWT, encryption)
- `references/performance.md` - Performance optimization (caching, indexing, lazy loading)
- `references/i18n.md` - Internationalization and localization
- `references/templates.md` - Ready-to-use code templates (auth, file upload, WebSocket, pagination)

Use the scripts in `scripts/` for common tasks:
- `scripts/create_model.py` - Generate model, schema, and route files
- `scripts/security_check.py` - Automated security vulnerability scanner

## Self-Check & Quality Assurance

**IMPORTANT: Before completing any project, always run security checks:**

```bash
# Run security self-check
python scripts/security_check.py ./project-directory

# This checks for:
# - Hardcoded secrets and API keys
# - Exposed database connection strings
# - SQL injection patterns
# - XSS vulnerabilities
# - Missing .gitignore entries
```

### Pre-Deployment Checklist

Before deploying, verify:
- [ ] All secrets use environment variables (`${VAR_NAME}`)
- [ ] No hardcoded passwords or API keys
- [ ] Database URLs use placeholders, not credentials
- [ ] `.env` is in `.gitignore`
- [ ] Security headers configured
- [ ] Input validation on all endpoints
