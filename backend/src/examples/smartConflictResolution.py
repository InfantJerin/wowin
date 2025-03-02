from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, Boolean, create_engine, select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./concurrency_test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define User model as an example
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)  # Version for optimistic locking
    last_modified = Column(String)  # Store last modified timestamp
    field_updates = Column(String)  # Store history of field updates as JSON

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserCreate(UserBase):
    username: str
    email: str

class UserUpdate(UserBase):
    version: int

class UserRead(UserBase):
    id: int
    version: int
    last_modified: str
    
    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new user
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=True,
        version=1,
        last_modified=datetime.now().isoformat(),
        field_updates=json.dumps({})
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Smart update function with field-level conflict resolution
@app.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    # Get the current user record
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the version matches
    current_version = db_user.version
    client_version = user_update.version
    
    # Get the updated fields (exclude version)
    update_data = user_update.dict(exclude_unset=True)
    provided_fields = {k: v for k, v in update_data.items() if k != "version" and v is not None}
    
    # If no version mismatch, simple update
    if current_version == client_version:
        # Update user fields
        for field, value in provided_fields.items():
            setattr(db_user, field, value)
        
        # Record this update in field_updates history
        field_history = json.loads(db_user.field_updates or "{}")
        timestamp = datetime.now().isoformat()
        
        for field in provided_fields:
            if field not in field_history:
                field_history[field] = []
            field_history[field].append({"version": current_version + 1, "timestamp": timestamp})
        
        # Increment version and update
        db_user.version = current_version + 1
        db_user.last_modified = timestamp
        db_user.field_updates = json.dumps(field_history)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    # Version mismatch: implement smart conflict resolution
    else:
        # Get field update history
        field_history = json.loads(db_user.field_updates or "{}")
        
        # Check if any of the requested fields were modified since client's version
        conflicting_fields = []
        for field in provided_fields:
            if field in field_history:
                # Check if this field was modified in versions after client's version
                recent_changes = [change for change in field_history[field] 
                                 if change["version"] > client_version]
                if recent_changes:
                    conflicting_fields.append(field)
        
        # If there are conflicting fields, return error with details
        if conflicting_fields:
            raise HTTPException(
                status_code=409, 
                detail={
                    "message": "Conflict detected",
                    "current_version": db_user.version,
                    "conflicting_fields": conflicting_fields,
                    "current_values": {field: getattr(db_user, field) for field in conflicting_fields}
                }
            )
        
        # No conflicts - can update non-conflicting fields
        timestamp = datetime.now().isoformat()
        
        # Update non-conflicting fields
        for field, value in provided_fields.items():
            setattr(db_user, field, value)
            
            # Record this update in field history
            if field not in field_history:
                field_history[field] = []
            field_history[field].append({"version": db_user.version + 1, "timestamp": timestamp})
        
        # Increment version and update
        db_user.version = db_user.version + 1
        db_user.last_modified = timestamp
        db_user.field_updates = json.dumps(field_history)
        
        db.commit()
        db.refresh(db_user)
        return db_user

# Get user by ID
@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Get conflict resolution guidance
@app.get("/conflict-resolution-guide")
def get_conflict_resolution_guide():
    return {
        "strategies": [
            {
                "name": "Auto-merge",
                "description": "Automatically merge non-conflicting fields and only require resolution for conflicting ones",
                "implementation": "Already implemented in the API"
            },
            {
                "name": "Last-writer-wins",
                "description": "Simply overwrite with the latest update (can be enabled as an option in the API)",
                "client_implementation": "Send update with force=True parameter"
            },
            {
                "name": "Manual resolution",
                "description": "Present conflicts to the user to manually decide which values to keep",
                "client_implementation": "Use the conflict response details to show UI for manual resolution"
            }
        ]
    }