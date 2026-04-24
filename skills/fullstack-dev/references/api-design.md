# API Design Patterns

## RESTful Conventions

### HTTP Methods
- `GET` - Retrieve resources (idempotent, safe)
- `POST` - Create new resources
- `PUT` - Replace entire resource
- `PATCH` - Partial update
- `DELETE` - Remove resource

### URL Structure
```
GET    /api/v1/users           # List users
POST   /api/v1/users           # Create user
GET    /api/v1/users/{id}      # Get specific user
PUT    /api/v1/users/{id}      # Update user
DELETE /api/v1/users/{id}      # Delete user
GET    /api/v1/users/me        # Current user (special case)
```

### Response Codes
- `200` - Success (GET, PUT, PATCH)
- `201` - Created (POST)
- `204` - No Content (DELETE)
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Server Error

## Pagination

```python
from fastapi import Query
from typing import List, Any

def paginate(
    items: List[Any],
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> dict:
    return {
        "items": items[skip : skip + limit],
        "total": len(items),
        "skip": skip,
        "limit": limit
    }
```

## Filtering & Sorting

```python
@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc")
):
    query = db.query(User)
    
    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    order_column = getattr(User, sort_by)
    if sort_order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())
    
    return query.all()
```

## Error Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

# Usage
raise AppException(status_code=404, detail="User not found")
```

## Request Validation

```python
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
```
