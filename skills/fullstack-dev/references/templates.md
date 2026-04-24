# Code Templates

This file contains ready-to-use code templates for common full-stack patterns.

---

## Authentication System

### Complete Auth Implementation

**Backend: User Model**

```python
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posts = relationship("Post", back_populates="author", lazy="dynamic")
    
    def __repr__(self):
        return f"<User {self.email}>"
```

**Backend: Auth Routes**

```python
# backend/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token,
    create_refresh_token
)
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if user exists
    existing = await db.execute(select(User).where(User.email == user_in.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        name=user_in.name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get tokens."""
    # Find user
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    payload = verify_token(refresh_token, settings.SECRET_KEY)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = await db.get(User, int(user_id))
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return {
        "access_token": create_access_token({"sub": str(user.id)}),
        "refresh_token": create_refresh_token({"sub": str(user.id)}),
        "token_type": "bearer"
    }
```

**Frontend: Auth Context**

```tsx
// frontend/src/contexts/AuthContext.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

interface User {
  id: number;
  email: string;
  name: string;
  is_superuser: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  
  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUser();
    } else {
      setIsLoading(false);
    }
  }, []);
  
  const fetchUser = async () => {
    try {
      const response = await api.get<User>('/users/me');
      setUser(response.data);
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setIsLoading(false);
    }
  };
  
  const login = async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    
    const { access_token, refresh_token } = response.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    await fetchUser();
    router.push('/dashboard');
  };
  
  const register = async (email: string, password: string, name: string) => {
    await api.post('/auth/register', { email, password, name });
    await login(email, password);
  };
  
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    router.push('/login');
  };
  
  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      isAuthenticated: !!user,
      login,
      register,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

---

## File Upload

### Backend: File Upload Handler

```python
# backend/app/api/v1/endpoints/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path
import uuid
import aiofiles
from PIL import Image
from app.core.config import settings

router = APIRouter(prefix="/upload", tags=["File Upload"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(filename: str, content_type: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type {ext} not allowed")
    return ext

@router.post("/single")
async def upload_single(file: UploadFile = File(...)):
    """Upload a single file."""
    ext = validate_file(file.filename, file.content_type)
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{ext}"
    filepath = Path(settings.UPLOAD_DIR) / filename
    
    # Save file
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, "File too large")
        await f.write(content)
    
    return {
        "id": file_id,
        "filename": filename,
        "original_name": file.filename,
        "size": len(content),
        "url": f"/api/v1/upload/{filename}"
    }

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    width: int = None,
    height: int = None
):
    """Upload and optionally resize an image."""
    ext = validate_file(file.filename, file.content_type)
    
    if not ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        raise HTTPException(400, "Only image files allowed")
    
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{ext}"
    filepath = Path(settings.UPLOAD_DIR) / filename
    
    # Process image
    content = await file.read()
    image = Image.open(io.BytesIO(content))
    
    if width or height:
        image.thumbnail((width or image.width, height or image.height))
    
    image.save(filepath, quality=85, optimize=True)
    
    return {
        "id": file_id,
        "filename": filename,
        "width": image.width,
        "height": image.height,
        "url": f"/api/v1/upload/{filename}"
    }

@router.get("/{filename}")
async def download_file(filename: str):
    """Download a file."""
    filepath = Path(settings.UPLOAD_DIR) / filename
    if not filepath.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(filepath)
```

**Frontend: File Upload Component**

```tsx
// frontend/src/components/FileUpload.tsx
'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onUpload: (files: File[]) => Promise<void>;
  accept?: Record<string, string[]>;
  maxFiles?: number;
  maxSize?: number;
  className?: string;
}

export function FileUpload({
  onUpload,
  accept = { 'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'] },
  maxFiles = 1,
  maxSize = 10 * 1024 * 1024,
  className,
}: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [previews, setPreviews] = useState<string[]>([]);
  
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    
    // Create previews
    const newPreviews = acceptedFiles.map(file => URL.createObjectURL(file));
    setPreviews(prev => [...prev, ...newPreviews]);
    
    try {
      await onUpload(acceptedFiles);
    } finally {
      setUploading(false);
    }
  }, [onUpload]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxFiles,
    maxSize,
  });
  
  const removePreview = (index: number) => {
    URL.revokeObjectURL(previews[index]);
    setPreviews(prev => prev.filter((_, i) => i !== index));
  };
  
  return (
    <div className={cn("space-y-4", className)}>
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
          isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25",
          uploading && "opacity-50 pointer-events-none"
        )}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-sm text-muted-foreground">
          {isDragActive ? "Drop files here" : "Drag & drop files, or click to select"}
        </p>
        <p className="text-xs text-muted-foreground mt-2">
          Max {maxFiles} file(s), up to {maxSize / 1024 / 1024}MB each
        </p>
      </div>
      
      {previews.length > 0 && (
        <div className="grid grid-cols-4 gap-4">
          {previews.map((preview, index) => (
            <div key={preview} className="relative group">
              <img
                src={preview}
                alt={`Preview ${index + 1}`}
                className="w-full h-24 object-cover rounded-lg"
              />
              <button
                onClick={() => removePreview(index)}
                className="absolute -top-2 -right-2 p-1 bg-destructive text-destructive-foreground rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## WebSocket / Real-time

### Backend: WebSocket Handler

```python
# backend/app/api/v1/endpoints/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set
import json
from app.api.deps import get_current_user_ws

router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        # room_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        self.active_connections[room_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
    
    async def broadcast(self, room_id: str, message: dict, exclude: WebSocket = None):
        if room_id not in self.active_connections:
            return
        
        for connection in self.active_connections[room_id]:
            if connection != exclude:
                await connection.send_json(message)
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/chat/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: str,
    # user: User = Depends(get_current_user_ws)  # For auth
):
    await manager.connect(websocket, room_id)
    
    try:
        # Send join notification
        await manager.broadcast(room_id, {
            "type": "user_joined",
            "room_id": room_id,
        }, exclude=websocket)
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Broadcast message to room
            await manager.broadcast(room_id, {
                "type": "message",
                "content": message.get("content"),
                "room_id": room_id,
                # "user_id": user.id,
                # "user_name": user.name,
            })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(room_id, {
            "type": "user_left",
            "room_id": room_id,
        })
```

**Frontend: WebSocket Hook**

```typescript
// frontend/src/hooks/useWebSocket.ts
import { useEffect, useRef, useCallback, useState } from 'react';

interface UseWebSocketOptions {
  onMessage?: (data: any) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export function useWebSocket(
  url: string,
  options: UseWebSocketOptions = {}
) {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
  } = options;
  
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  
  const connect = useCallback(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      setIsConnected(true);
      reconnectAttempts.current = 0;
      onConnect?.();
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage?.(data);
    };
    
    ws.onclose = () => {
      setIsConnected(false);
      onDisconnect?.();
      
      // Attempt reconnect
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current++;
        setTimeout(connect, reconnectInterval);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    wsRef.current = ws;
  }, [url, onMessage, onConnect, onDisconnect, reconnectInterval, maxReconnectAttempts]);
  
  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);
  
  const disconnect = useCallback(() => {
    wsRef.current?.close();
  }, []);
  
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);
  
  return { isConnected, send, disconnect, reconnect: connect };
}

// Usage
function ChatRoom({ roomId }: { roomId: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  
  const { isConnected, send } = useWebSocket(
    `ws://localhost:8000/api/v1/ws/chat/${roomId}`,
    {
      onMessage: (data) => {
        if (data.type === 'message') {
          setMessages(prev => [...prev, data]);
        }
      },
    }
  );
  
  const sendMessage = (content: string) => {
    send({ type: 'message', content });
  };
  
  return (
    <div>
      <div>Connected: {isConnected ? 'Yes' : 'No'}</div>
      {/* messages list and input */}
    </div>
  );
}
```

---

## Pagination

### Backend: Paginated Response

```python
# backend/app/schemas/common.py
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

# backend/app/api/v1/endpoints/items.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.schemas.common import PaginatedResponse

router = APIRouter()

@router.get("/items", response_model=PaginatedResponse[Item])
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Get paginated list of items."""
    query = select(Item)
    count_query = select(func.count()).select_from(Item)
    
    # Apply filters
    if search:
        query = query.where(Item.name.ilike(f"%{search}%"))
        count_query = count_query.where(Item.name.ilike(f"%{search}%"))
    
    # Get total count
    total = await db.scalar(count_query)
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    items = result.scalars().all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )
```

**Frontend: Pagination Component**

```tsx
// frontend/src/components/Pagination.tsx
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  showPageNumbers?: boolean;
}

export function Pagination({
  page,
  totalPages,
  onPageChange,
  showPageNumbers = true,
}: PaginationProps) {
  const pages = getPageNumbers(page, totalPages);
  
  return (
    <nav className="flex items-center justify-center gap-2">
      <Button
        variant="outline"
        size="icon"
        disabled={page === 1}
        onClick={() => onPageChange(page - 1)}
      >
        <ChevronLeft className="h-4 w-4" />
      </Button>
      
      {showPageNumbers && pages.map((p, i) => (
        p === '...' ? (
          <span key={`ellipsis-${i}`} className="px-2">...</span>
        ) : (
          <Button
            key={p}
            variant={p === page ? 'default' : 'outline'}
            size="icon"
            onClick={() => onPageChange(p as number)}
          >
            {p}
          </Button>
        )
      ))}
      
      <Button
        variant="outline"
        size="icon"
        disabled={page === totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        <ChevronRight className="h-4 w-4" />
      </Button>
    </nav>
  );
}

function getPageNumbers(current: number, total: number): (number | string)[] {
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1);
  }
  
  if (current <= 3) {
    return [1, 2, 3, 4, '...', total];
  }
  
  if (current >= total - 2) {
    return [1, '...', total - 3, total - 2, total - 1, total];
  }
  
  return [1, '...', current - 1, current, current + 1, '...', total];
}
```

---

## Email Templates

### Backend: Email Service

```python
# backend/app/services/email.py
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader("templates/email"))
    
    async def send_email(
        self,
        to: str,
        subject: str,
        template_name: str,
        context: dict
    ):
        """Send templated email."""
        # Render templates
        template = self.env.get_template(template_name)
        html_content = template.render(**context)
        text_content = self._html_to_text(html_content)
        
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = settings.EMAIL_FROM
        message["To"] = to
        message["Subject"] = subject
        
        message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))
        
        # Send
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
        )
    
    async def send_welcome_email(self, user: User):
        await self.send_email(
            to=user.email,
            subject="Welcome to Our App!",
            template_name="welcome.html",
            context={"user": user, "app_name": settings.PROJECT_NAME}
        )
    
    async def send_password_reset(self, user: User, reset_url: str):
        await self.send_email(
            to=user.email,
            subject="Reset Your Password",
            template_name="password_reset.html",
            context={"user": user, "reset_url": reset_url}
        )

email_service = EmailService()
```

**Email Template**

```html
<!-- templates/email/welcome.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: -apple-system, sans-serif; line-height: 1.6; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
              color: white; padding: 40px 20px; text-align: center; }
    .content { padding: 40px 20px; }
    .button { display: inline-block; padding: 12px 24px; 
              background: #667eea; color: white; text-decoration: none; 
              border-radius: 6px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Welcome to {{ app_name }}!</h1>
    </div>
    <div class="content">
      <p>Hi {{ user.name }},</p>
      <p>Thank you for joining us. We're excited to have you on board!</p>
      <p>Here's what you can do next:</p>
      <ul>
        <li>Complete your profile</li>
        <li>Explore our features</li>
        <li>Connect with others</li>
      </ul>
      <p style="text-align: center; margin-top: 30px;">
        <a href="{{ dashboard_url }}" class="button">Get Started</a>
      </p>
    </div>
  </div>
</body>
</html>
```
