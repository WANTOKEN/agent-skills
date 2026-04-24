# Database Patterns & Migrations

## SQLAlchemy Setup

### Database Connection (`app/core/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Model Patterns

### Base Model with Timestamps

```python
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Soft Delete

```python
from sqlalchemy import Column, Boolean, DateTime
from sqlalchemy.sql import func

class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = func.now()
```

### Relationships

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    posts = relationship("Post", back_populates="author", lazy="dynamic")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
```

## Alembic Migrations

### Setup

```bash
alembic init alembic
```

### Configure `alembic.ini`

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

### Configure `alembic/env.py`

```python
from app.core.database import Base
from app.models import *  # Import all models

target_metadata = Base.metadata
```

### Commands

```bash
# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Query Optimization

### Eager Loading

```python
from sqlalchemy.orm import joinedload, selectinload

# Joined load (JOIN)
users = db.query(User).options(joinedload(User.posts)).all()

# Select in load (separate queries)
users = db.query(User).options(selectinload(User.posts)).all()
```

### Indexing

```python
from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"
    
    email = Column(String, index=True)  # Single column index
    name = Column(String)
    
    __table_args__ = (
        Index('ix_user_email_name', 'email', 'name'),  # Composite index
    )
```

## Connection Pooling

```python
engine = create_engine(
    database_url,
    pool_size=10,          # Number of connections to keep
    max_overflow=20,       # Additional connections allowed
    pool_timeout=30,       # Seconds to wait for connection
    pool_recycle=1800,     # Recycle connections after 30 min
)
```
