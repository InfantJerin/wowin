from typing import Generator
from functools import lru_cache
import logging

from fastapi import Depends, FastAPI, Request
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Create separate engines for read and write operations
write_engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections after 5 minutes
)

# Read-only engine with larger pool for higher read traffic
read_engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Larger pool for read operations
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
    execution_options={"readonly": True}  # Mark connections as read-only
)

# Create session factories
WriteSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=write_engine)
ReadSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=read_engine)

Base = declarative_base()

# For PostgreSQL: Set connections as read-only at the database level
@event.listens_for(read_engine, "connect")
def set_readonly_connection(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    cursor.close()

# Database dependencies for FastAPI
def get_write_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session for write operations.
    """
    db = WriteSessionLocal()
    try:
        logger.debug("Using WRITE connection")
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_read_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a read-only database session.
    No commit needed as sessions are read-only.
    """
    db = ReadSessionLocal()
    try:
        logger.debug("Using READ connection")
        yield db
        # No commit needed for read-only sessions
    except Exception:
        db.rollback()  # Still rollback in case of errors to release locks
        raise
    finally:
        db.close()

# Function to determine which db pool to use based on request method
def get_db_for_request(request: Request) -> Generator[Session, None, None]:
    """
    FastAPI dependency that selects the appropriate db session based on HTTP method.
    GET, HEAD and OPTIONS requests use read-only connections.
    All other methods use write connections.
    """
    if request.method.upper() in ("GET", "HEAD", "OPTIONS"):
        db_dependency = get_read_db
    else:
        db_dependency = get_write_db
    
    # Create a new dependency generator instance and return it
    return next(db_dependency())

# FastAPI app and example routes
app = FastAPI()

@app.get("/items/")
def read_items(db: Session = Depends(get_read_db)):
    """
    Endpoint that explicitly uses the read-only connection pool.
    """
    # Example read operation
    # items = db.query(Item).all()
    return {"message": "Using read-only connection pool"}

@app.post("/items/")
def create_item(item_data: dict, db: Session = Depends(get_write_db)):
    """
    Endpoint that explicitly uses the write connection pool.
    """
    # Example write operation
    # new_item = Item(**item_data)
    # db.add(new_item)
    return {"message": "Using write connection pool"}

@app.get("/auto-items/")
def auto_read_items(db: Session = Depends(get_db_for_request)):
    """
    Endpoint that automatically uses the right connection pool
    based on the HTTP method.
    """
    # This will use read-only connection for GET requests
    return {"message": "Automatically chose connection pool based on method"}

@app.post("/auto-items/")
def auto_create_item(item_data: dict, db: Session = Depends(get_db_for_request)):
    """
    Endpoint that automatically uses the right connection pool
    based on the HTTP method.
    """
    # This will use write connection for POST requests
    return {"message": "Automatically chose connection pool based on method"}

# Connection pool statistics
@app.get("/db-stats/")
def get_db_stats():
    """
    Get statistics about the database connection pools.
    """
    write_stats = {
        "pool_size": write_engine.pool.size(),
        "checkedin": write_engine.pool.checkedin(),
        "overflow": write_engine.pool.overflow(),
        "checkedout": write_engine.pool.checkedout(),
    }
    
    read_stats = {
        "pool_size": read_engine.pool.size(),
        "checkedin": read_engine.pool.checkedin(),
        "overflow": read_engine.pool.overflow(),
        "checkedout": read_engine.pool.checkedout(),
    }
    
    return {
        "write_pool": write_stats,
        "read_pool": read_stats
    }

# Optional: Add read replica support
@lru_cache()
def get_read_replica_engines(num_replicas=3):
    """
    Create multiple read replica engines if you have read replicas.
    This is useful for distributing read queries across multiple database servers.
    """
    replicas = []
    # Example replica connection strings - in production these would come from config
    replica_urls = [
        f"postgresql://readonly:password@replica-{i}.example.com/dbname" 
        for i in range(1, num_replicas + 1)
    ]
    
    for url in replica_urls:
        engine = create_engine(
            url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            execution_options={"readonly": True}
        )
        replicas.append(engine)
    
    return replicas

# Round-robin selection of read replicas
replica_index = 0
def get_next_read_replica_db():
    """
    FastAPI dependency that provides a session from the next read replica
    in a round-robin fashion.
    """
    global replica_index
    replicas = get_read_replica_engines()
    
    if not replicas:
        # Fall back to main read pool if no replicas configured
        return next(get_read_db())
    
    # Round-robin selection
    engine = replicas[replica_index % len(replicas)]
    replica_index += 1
    
    # Create session from the selected replica
    ReplicaSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = ReplicaSession()
    
    try:
        logger.debug(f"Using READ REPLICA {replica_index-1}")
        yield db
    finally:
        db.close()