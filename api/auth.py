# Standard library imports
from datetime import datetime, timedelta
from typing import Optional
import logging

# Third-party imports
from jose import JWTError, jwt  # For JWT token handling
from passlib.context import CryptContext  # For password hashing
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer  # FastAPI's OAuth2 with Bearer token
from sqlalchemy.orm import Session

# Local imports
from .database import SessionLocal
from .models import User

# JWT Configuration
SECRET_KEY = "your-secret-key-keep-it-secret"  # In production, move this to environment variables
ALGORITHM = "HS256"  # HMAC with SHA-256 hash algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes

# Password hashing configuration using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 configuration with Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Set up logging for authentication operations
logger = logging.getLogger(__name__)

def get_db():
    """Database dependency injection.
    
    Creates a new database session for each request and ensures it's closed after use.
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.
    
    Args:
        plain_password (str): The password in plain text
        hashed_password (str): The hashed password to compare against
    
    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash using bcrypt.
    
    Args:
        password (str): Plain text password to hash
    
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)

def get_user(db: Session, username: str) -> Optional[User]:
    """Retrieve a user from the database by username.
    
    Args:
        db (Session): Database session
        username (str): Username to look up
    
    Returns:
        Optional[User]: User object if found, None otherwise
    """
    logger.debug(f"Fetching user {username} from database")
    return db.query(User).filter(User.name == username).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password.
    
    Args:
        db (Session): Database session
        username (str): Username to authenticate
        password (str): Password to verify
    
    Returns:
        Optional[User]: Authenticated user object if successful, None otherwise
    """
    logger.debug(f"Authenticating user {username}")
    user = get_user(db, username)
    if not user:
        logger.warning(f"User {username} not found")
        return None
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Password verification failed for user {username}")
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT access token.
    
    Args:
        data (dict): Payload data to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time delta
    
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Access token created for {data.get('sub')}")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """FastAPI dependency that validates JWT token and returns current user.
    
    Args:
        token (str): JWT token from request (injected by FastAPI)
        db (Session): Database session (injected by FastAPI)
    
    Returns:
        User: Current authenticated user
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get("sub")
        if name is None:
            logger.error("Token payload does not contain 'sub'")
            raise credentials_exception
    except JWTError:
        logger.error("JWT decoding failed")
        raise credentials_exception
    
    user = get_user(db, name)
    if user is None:
        logger.error(f"User {name} not found after token decoding")
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """FastAPI dependency that ensures the current user is active.
    
    Args:
        current_user (User): Current authenticated user (injected by FastAPI)
    
    Returns:
        User: Current active user
    
    Raises:
        HTTPException: If user is inactive
    """
    return current_user

