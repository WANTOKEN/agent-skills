#!/usr/bin/env python3
"""
Generate model, schema, and route files for a new resource.
Usage: python create_model.py <model_name> [fields]
Example: python create_model.py Product name:str price:float quantity:int
"""

import sys
import os
from pathlib import Path

def to_camel_case(snake_str):
    """Convert snake_case to CamelCase"""
    return ''.join(x.title() for x in snake_str.split('_'))

def to_snake_case(name):
    """Convert CamelCase to snake_case"""
    return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')

def parse_field(field_str):
    """Parse field definition like 'name:str' or 'price:float'"""
    parts = field_str.split(':')
    name = parts[0]
    field_type = parts[1] if len(parts) > 1 else 'str'
    return name, field_type

def get_sqlalchemy_type(field_type):
    """Map Python types to SQLAlchemy types"""
    type_map = {
        'str': 'String',
        'int': 'Integer',
        'float': 'Float',
        'bool': 'Boolean',
        'datetime': 'DateTime',
        'date': 'Date',
    }
    return type_map.get(field_type, 'String')

def generate_model(model_name, fields):
    """Generate SQLAlchemy model code"""
    class_name = to_camel_case(model_name)
    
    field_definitions = []
    for name, field_type in fields:
        sa_type = get_sqlalchemy_type(field_type)
        if name == 'id':
            field_definitions.append(f"    {name} = Column({sa_type}, primary_key=True, index=True)")
        elif name.endswith('_id'):
            field_definitions.append(f"    {name} = Column({sa_type}, ForeignKey('users.id'))")
        else:
            field_definitions.append(f"    {name} = Column({sa_type})")
    
    return f'''from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class {class_name}(Base):
    __tablename__ = "{model_name}s"
    
{chr(10).join(field_definitions)}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
'''

def generate_schema(model_name, fields):
    """Generate Pydantic schema code"""
    class_name = to_camel_case(model_name)
    
    field_definitions = [f"    {name}: {field_type}" for name, field_type in fields if name != 'id']
    
    return f'''from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class {class_name}Base(BaseModel):
{chr(10).join(field_definitions) if field_definitions else "    pass"}

class {class_name}Create({class_name}Base):
    pass

class {class_name}Update(BaseModel):
{chr(10).join([f"    {name}: Optional[{field_type}] = None" for name, field_type in fields if name != 'id']) if any(name != 'id' for name, _ in fields) else "    pass"}

class {class_name}Response({class_name}Base):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
'''

def generate_router(model_name, fields):
    """Generate FastAPI router code"""
    class_name = to_camel_case(model_name)
    
    return f'''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user
from app.models.{model_name} import {class_name}
from app.schemas.{model_name} import {class_name}Create, {class_name}Update, {class_name}Response

router = APIRouter()

@router.get("/", response_model=List[{class_name}Response])
def list_{model_name}s(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    return db.query({class_name}).offset(skip).limit(limit).all()

@router.get("/{{{model_name}_id}}", response_model={class_name}Response)
def get_{model_name}({model_name}_id: int, db: Session = Depends(get_db)):
    item = db.query({class_name}).filter({class_name}.id == {model_name}_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    return item

@router.post("/", response_model={class_name}Response)
def create_{model_name}({model_name}_in: {class_name}Create, db: Session = Depends(get_db)):
    db_item = {class_name}(**{model_name}_in.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{{{model_name}_id}}", response_model={class_name}Response)
def update_{model_name}(
    {model_name}_id: int,
    {model_name}_in: {class_name}Update,
    db: Session = Depends(get_db)
):
    item = db.query({class_name}).filter({class_name}.id == {model_name}_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    for field, value in {model_name}_in.dict(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/{{{model_name}_id}}")
def delete_{model_name}({model_name}_id: int, db: Session = Depends(get_db)):
    item = db.query({class_name}).filter({class_name}.id == {model_name}_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{class_name} not found")
    db.delete(item)
    db.commit()
    return {{"message": "{class_name} deleted successfully"}}
'''

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    model_name = to_snake_case(sys.argv[1])
    fields = [('id', 'int')]
    
    for field_str in sys.argv[2:]:
        fields.append(parse_field(field_str))
    
    # Create output directory
    output_dir = Path.cwd() / "generated" / model_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate files
    (output_dir / f"model_{model_name}.py").write_text(generate_model(model_name, fields))
    (output_dir / f"schema_{model_name}.py").write_text(generate_schema(model_name, fields))
    (output_dir / f"router_{model_name}.py").write_text(generate_router(model_name, fields))
    
    print(f"Generated files in {output_dir}:")
    print(f"  - model_{model_name}.py")
    print(f"  - schema_{model_name}.py")
    print(f"  - router_{model_name}.py")

if __name__ == "__main__":
    main()
