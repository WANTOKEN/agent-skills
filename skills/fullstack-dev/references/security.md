# Security Best Practices

## Authentication Security

### Password Security

```python
# backend/app/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password hashing
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Secure password generation
def generate_secure_password(length: int = 16) -> str:
    return secrets.token_urlsafe(length)

# JWT Token
def create_access_token(
    data: dict,
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: timedelta = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

def verify_token(token: str, secret_key: str) -> dict | None:
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
```

### JWT Best Practices

```python
# Use short expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived access token
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Long-lived refresh token

# Always use HTTPS in production
# Store tokens securely (httpOnly cookies preferred)
# Implement token revocation for logout

# backend/app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    payload = verify_token(token, settings.SECRET_KEY)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    user = await get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
```

---

## Input Validation & Sanitization

### Pydantic Validation

```python
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain special character')
        return v
    
    @validator('name')
    def sanitize_name(cls, v):
        # Remove potential XSS characters
        return re.sub(r'[<>"\'&]', '', v.strip())

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., max_length=10000)
    
    @validator('title', 'content')
    def sanitize_html(cls, v):
        # Basic HTML sanitization
        return re.sub(r'<script.*?</script>', '', v, flags=re.IGNORECASE | re.DOTALL)
```

### SQL Injection Prevention

```python
# ALWAYS use parameterized queries
from sqlalchemy import text

# ❌ BAD - Vulnerable to SQL injection
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ GOOD - Parameterized query
from sqlalchemy import select
query = select(User).where(User.email == email)

# ✅ GOOD - Raw SQL with parameters
query = text("SELECT * FROM users WHERE email = :email")
result = await db.execute(query, {"email": email})
```

---

## XSS Prevention

### Frontend Sanitization

```typescript
// frontend/src/lib/sanitize.ts
import DOMPurify from 'dompurify';

export function sanitizeHTML(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br'],
    ALLOWED_ATTR: ['href', 'target'],
  });
}

// Usage in React
function SafeHTML({ content }: { content: string }) {
  return (
    <div 
      dangerouslySetInnerHTML={{ 
        __html: sanitizeHTML(content) 
      }} 
    />
  );
}
```

### Content Security Policy

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self';
      connect-src 'self' https://api.yourdomain.com;
      frame-ancestors 'none';
    `.replace(/\s{2,}/g, ' ').trim()
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  }
];

module.exports = {
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }];
  }
};
```

---

## CSRF Protection

### FastAPI CSRF

```python
# backend/app/middleware/csrf.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import secrets

class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF for safe methods
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return await call_next(request)
        
        # Skip for API token auth
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return await call_next(request)
        
        # Validate CSRF token
        csrf_token = request.headers.get('X-CSRF-Token')
        cookie_token = request.cookies.get('csrf_token')
        
        if not csrf_token or not cookie_token or csrf_token != cookie_token:
            raise HTTPException(status_code=403, detail="CSRF token invalid")
        
        return await call_next(request)

def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)
```

### Frontend CSRF

```typescript
// frontend/src/lib/api.ts
import axios from 'axios';

// Get CSRF token from cookie
function getCSRFToken(): string | null {
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  return match ? match[1] : null;
}

// Add CSRF token to requests
api.interceptors.request.use((config) => {
  if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.method?.toUpperCase() || '')) {
    const csrfToken = getCSRFToken();
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
  }
  return config;
});
```

---

## Rate Limiting

```python
# backend/app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to app
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# Usage on routes
@app.post("/auth/login")
@limiter.limit("5/minute")  # 5 requests per minute
async def login(request: Request, credentials: LoginRequest):
    # ... login logic
    pass

@app.post("/auth/register")
@limiter.limit("3/hour")  # 3 registrations per hour
async def register(request: Request, user: UserCreate):
    # ... registration logic
    pass
```

---

## Sensitive Data Handling

### Environment Variables

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Never hardcode secrets!
    SECRET_KEY: str = Field(..., min_length=32)  # Required
    DATABASE_URL: str
    API_KEY: str | None = None
    
    # Mask sensitive values in logs
    @property
    def safe_database_url(self) -> str:
        # postgresql://user:***@host/db (password masked)
        if '@' in self.DATABASE_URL:
            parts = self.DATABASE_URL.split('@')
            credentials = parts[0].split(':')
            if len(credentials) == 3:
                return f"{credentials[0]}:{credentials[1]}:***@{parts[1]}"
        return self.DATABASE_URL
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

### Data Encryption

```python
# backend/app/core/encryption.py
from cryptography.fernet import Fernet
import base64
import os

class DataEncryption:
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.fernet.decrypt(encrypted_data.encode()).decode()

# Generate key (run once, store securely)
def generate_encryption_key() -> bytes:
    return Fernet.generate_key()

# Usage for sensitive fields
encryption = DataEncryption(settings.ENCRYPTION_KEY)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    _ssn = Column("ssn", String)  # Encrypted SSN
    
    @property
    def ssn(self) -> str:
        return encryption.decrypt(self._ssn) if self._ssn else None
    
    @ssn.setter
    def ssn(self, value: str):
        self._ssn = encryption.encrypt(value)
```

---

## Security Headers Checklist

| Header | Value | Purpose |
|--------|-------|---------|
| Content-Security-Policy | `default-src 'self'` | XSS prevention |
| X-Content-Type-Options | `nosniff` | MIME sniffing prevention |
| X-Frame-Options | `DENY` | Clickjacking prevention |
| X-XSS-Protection | `1; mode=block` | XSS filter (legacy) |
| Strict-Transport-Security | `max-age=31536000` | HTTPS enforcement |
| Referrer-Policy | `strict-origin-when-cross-origin` | Referrer control |
| Permissions-Policy | `geolocation=(), camera=()` | Feature restriction |

---

## Security Audit Checklist

### Authentication
- [ ] Passwords hashed with bcrypt/argon2
- [ ] JWT tokens have short expiration
- [ ] Refresh tokens stored securely
- [ ] Login rate limiting enabled
- [ ] Account lockout after failed attempts

### Authorization
- [ ] Role-based access control implemented
- [ ] Resource ownership verified
- [ ] API endpoints have proper auth checks

### Input Handling
- [ ] All input validated with Pydantic
- [ ] SQL queries use parameterization
- [ ] File uploads validated (type, size)
- [ ] HTML content sanitized

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] HTTPS enforced in production
- [ ] Secrets in environment variables
- [ ] No sensitive data in logs

### Headers & CORS
- [ ] Security headers configured
- [ ] CORS restricted to known origins
- [ ] CSRF protection for session auth
