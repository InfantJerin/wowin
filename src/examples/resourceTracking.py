from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import Dict, List, Optional, Set
import json
from datetime import datetime, timedelta
import asyncio
import redis

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./resource_tracking.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis for real-time presence tracking
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    
class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    data = Column(String)
    version = Column(Integer, default=1)
    
class ResourceActivity(Base):
    __tablename__ = "resource_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    resource = relationship("Resource")
    user = relationship("User")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: str
    
class UserCreate(UserBase):
    pass
    
class UserRead(UserBase):
    id: int
    
    class Config:
        orm_mode = True
        
class ResourceBase(BaseModel):
    name: str
    
class ResourceCreate(ResourceBase):
    data: str
    
class ResourceUpdate(BaseModel):
    data: Optional[str] = None
    version: int
    
class ResourceRead(ResourceBase):
    id: int
    version: int
    data: str
    
    class Config:
        orm_mode = True
        
class ActiveUserInfo(BaseModel):
    user_id: int
    username: str
    started_at: str
    last_activity: str
    
class ResourceActiveUsers(BaseModel):
    resource_id: int
    resource_name: str
    active_users: List[ActiveUserInfo]

# FastAPI app
app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Helper for current user (replace with actual auth in production)
def get_current_user_id():
    # This would normally use OAuth or other auth
    return 1  # Mock user ID

# Redis key helpers
def get_resource_users_key(resource_id: int) -> str:
    return f"resource:{resource_id}:active_users"

def get_user_resources_key(user_id: int) -> str:
    return f"user:{user_id}:active_resources"

# Presence tracking functions
def track_user_on_resource(resource_id: int, user_id: int, db: Session):
    # Record in database
    activity = db.query(ResourceActivity).filter(
        ResourceActivity.resource_id == resource_id,
        ResourceActivity.user_id == user_id,
        ResourceActivity.is_active == True
    ).first()
    
    now = datetime.utcnow()
    
    if not activity:
        # New activity
        activity = ResourceActivity(
            resource_id=resource_id,
            user_id=user_id,
            started_at=now,
            last_activity=now,
            is_active=True
        )
        db.add(activity)
    else:
        # Update last activity
        activity.last_activity = now
        
    db.commit()
    
    # Record in Redis for real-time access
    resource_key = get_resource_users_key(resource_id)
    user_key = get_user_resources_key(user_id)
    
    # Store in Redis with expiration (auto-cleanup after 5 minutes of inactivity)
    user_data = json.dumps({
        "user_id": user_id,
        "last_activity": now.isoformat()
    })
    
    redis_client.hset(resource_key, user_id, user_data)
    redis_client.expire(resource_key, 300)  # 5 minutes TTL
    
    # Track which resources user is viewing
    redis_client.sadd(user_key, resource_id)
    redis_client.expire(user_key, 300)  # 5 minutes TTL

def get_active_users_on_resource(resource_id: int, db: Session) -> List[ActiveUserInfo]:
    # First check Redis for real-time data
    resource_key = get_resource_users_key(resource_id)
    redis_users = redis_client.hgetall(resource_key)
    
    active_users = []
    
    if redis_users:
        # Get all user details from DB for users in Redis
        user_ids = [int(uid) for uid in redis_users.keys()]
        users = {
            u.id: u for u in 
            db.query(User).filter(User.id.in_(user_ids)).all()
        }
        
        for user_id_str, user_data_json in redis_users.items():
            user_id = int(user_id_str)
            user_data = json.loads(user_data_json)
            
            if user_id in users:
                # Clean up expired users (activity older than 5 minutes)
                last_activity = datetime.fromisoformat(user_data["last_activity"])
                if datetime.utcnow() - last_activity > timedelta(minutes=5):
                    redis_client.hdel(resource_key, user_id_str)
                    continue
                    
                active_users.append(ActiveUserInfo(
                    user_id=user_id,
                    username=users[user_id].username,
                    started_at=last_activity.isoformat(),  # Simplified, should be actual start time
                    last_activity=last_activity.isoformat()
                ))
    
    # If Redis has no data, fall back to database
    if not active_users:
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)
        
        activities = db.query(ResourceActivity).join(User).filter(
            ResourceActivity.resource_id == resource_id,
            ResourceActivity.is_active == True,
            ResourceActivity.last_activity >= cutoff_time
        ).all()
        
        for activity in activities:
            active_users.append(ActiveUserInfo(
                user_id=activity.user_id,
                username=activity.user.username,
                started_at=activity.started_at.isoformat(),
                last_activity=activity.last_activity.isoformat()
            ))
    
    return active_users

def mark_user_inactive(resource_id: int, user_id: int, db: Session):
    # Update database
    db.query(ResourceActivity).filter(
        ResourceActivity.resource_id == resource_id,
        ResourceActivity.user_id == user_id,
        ResourceActivity.is_active == True
    ).update({"is_active": False})
    
    db.commit()
    
    # Remove from Redis
    resource_key = get_resource_users_key(resource_id)
    user_key = get_user_resources_key(user_id)
    
    redis_client.hdel(resource_key, str(user_id))
    redis_client.srem(user_key, resource_id)

# Endpoints
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/resources/", response_model=ResourceRead)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    db_resource = Resource(
        name=resource.name,
        data=resource.data,
        version=1
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@app.get("/resources/{resource_id}", response_model=ResourceRead)
def get_resource(
    resource_id: int, 
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Track that this user is viewing the resource
    track_user_on_resource(resource_id, current_user_id, db)
    
    return resource

@app.get("/resources/{resource_id}/active-users", response_model=ResourceActiveUsers)
def get_resource_active_users(
    resource_id: int, 
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Include the current user in tracking
    track_user_on_resource(resource_id, current_user_id, db)
    
    # Get all active users
    active_users = get_active_users_on_resource(resource_id, db)
    
    return ResourceActiveUsers(
        resource_id=resource.id,
        resource_name=resource.name,
        active_users=active_users
    )

@app.patch("/resources/{resource_id}", response_model=ResourceRead)
def update_resource(
    resource_id: int, 
    resource_update: ResourceUpdate, 
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    # Update the resource with version checking
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Track this user
    track_user_on_resource(resource_id, current_user_id, db)
    
    # Version check
    if resource.version != resource_update.version:
        # Get the active users for conflict information
        active_users = get_active_users_on_resource(resource_id, db)
        other_users = [u for u in active_users if u.user_id != current_user_id]
        
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Version conflict",
                "current_version": resource.version,
                "your_version": resource_update.version,
                "other_active_users": [u.dict() for u in other_users]
            }
        )
    
    # Update the resource
    if resource_update.data is not None:
        resource.data = resource_update.data
    
    resource.version += 1
    db.commit()
    
    return resource

@app.post("/resources/{resource_id}/release")
def release_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    # Mark the user as no longer actively working on this resource
    mark_user_inactive(resource_id, current_user_id, db)
    return {"message": "Resource released successfully"}

# WebSocket for real-time presence updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, resource_id: int, user_id: int):
        await websocket.accept()
        
        if resource_id not in self.active_connections:
            self.active_connections[resource_id] = {}
            
        self.active_connections[resource_id][user_id] = websocket
    
    def disconnect(self, resource_id: int, user_id: int):
        if resource_id in self.active_connections:
            if user_id in self.active_connections[resource_id]:
                del self.active_connections[resource_id][user_id]
            
            if not self.active_connections[resource_id]:
                del self.active_connections[resource_id]
    
    async def broadcast_to_resource(self, resource_id: int, message: dict):
        if resource_id in self.active_connections:
            for websocket in self.active_connections[resource_id].values():
                await websocket.send_json(message)

manager = ConnectionManager()

# Background task to periodically update clients about active users
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_presence_updates())

async def periodic_presence_updates():
    db = SessionLocal()
    try:
        while True:
            # For each resource with active connections
            for resource_id in manager.active_connections:
                # Get all active users
                active_users = get_active_users_on_resource(resource_id, db)
                
                # Broadcast to all clients
                await manager.broadcast_to_resource(
                    resource_id, 
                    {
                        "type": "presence_update", 
                        "active_users": [u.dict() for u in active_users]
                    }
                )
            
            await asyncio.sleep(5)  # Update every 5 seconds
    finally:
        db.close()

@app.websocket("/ws/resources/{resource_id}/presence")
async def websocket_presence(websocket: WebSocket, resource_id: int, user_id: int = Depends(get_current_user_id)):
    db = SessionLocal()
    try:
        await manager.connect(websocket, resource_id, user_id)
        
        # Send initial presence data
        active_users = get_active_users_on_resource(resource_id, db)
        await websocket.send_json({
            "type": "presence_update",
            "active_users": [u.dict() for u in active_users]
        })
        
        # Track this user
        track_user_on_resource(resource_id, user_id, db)
        
        # Broadcast that this user joined
        await manager.broadcast_to_resource(
            resource_id,
            {
                "type": "user_joined",
                "user_id": user_id
            }
        )
        
        try:
            while True:
                # Keep connection alive and handle client messages
                data = await websocket.receive_text()
                if data == "ping":
                    # Update user activity timestamp
                    track_user_on_resource(resource_id, user_id, db)
                    await websocket.send_text("pong")
                
        except WebSocketDisconnect:
            manager.disconnect(resource_id, user_id)
            mark_user_inactive(resource_id, user_id, db)
            
            # Broadcast that this user left
            await manager.broadcast_to_resource(
                resource_id,
                {
                    "type": "user_left",
                    "user_id": user_id
                }
            )
    finally:
        db.close()