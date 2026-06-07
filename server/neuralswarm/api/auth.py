import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralswarm.database import get_db
from neuralswarm.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# JWT configuration
SECRET_KEY = "neuralswarm-dev-secret-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# --- Schemas ---

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: datetime


class UserCreate(BaseModel):
    username: str
    email: str = ""
    password: str
    display_name: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# --- Utilities ---

def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict:
    """Verify a JWT token and return its payload.

    Raises JWTError if the token is invalid or expired.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


# --- Endpoints ---

@router.post("/token", response_model=Token)
async def login_for_access_token(user_login: UserLogin):
    """Authenticate a user and return a JWT token.

    NOTE: This is a placeholder implementation. In production, it should
    look up the user from the database and verify credentials.
    """
    # Placeholder: accept any login for development
    access_token = create_access_token(subject=user_login.username)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register_user(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if username exists
    stmt = select(User).where(User.username == user_create.username)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Create user
    user = User(
        username=user_create.username,
        email=user_create.email or f"{user_create.username}@local",
        hashed_password=hash_password(user_create.password),
        display_name=user_create.display_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {"message": "User registered successfully", "username": user.username}


@router.post("/login")
async def login_user(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and return access + refresh tokens."""
    stmt = select(User).where(User.username == user_login.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    return {
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    }


@router.post("/refresh")
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    try:
        payload = verify_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = UUID(payload["sub"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )

    # Verify user exists
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token = create_access_token(subject=str(user_id))

    return {"data": {"access_token": access_token, "token_type": "bearer"}}
