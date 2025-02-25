from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import create_access_token, get_current_user, verify_password
from app.db.mongodb.users import get_user_by_email, create_user, get_user_by_username
from app.models.user import User, UserCreate, UserWithToken


router = APIRouter()


@router.post("/login", response_model=UserWithToken)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    Args:
        form_data: Username and password
        
    Returns:
        User info with access token
    """
    # Check if user exists by username
    user = await get_user_by_username(form_data.username)
    
    # If not found by username, try email
    if not user:
        user = await get_user_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    # Convert UserInDB to User and add token
    return UserWithToken(
        **User.from_orm(user).dict(),
        access_token=access_token,
        token_type="bearer",
        following_count=len(user.following),
        followers_count=len(user.followers)
    )


@router.post("/register", response_model=UserWithToken)
async def register(user_create: UserCreate) -> Any:
    """
    Register a new user.
    
    Args:
        user_create: User creation data
        
    Returns:
        User info with access token
    """
    # Check if user with this email already exists
    if await get_user_by_email(user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if user with this username already exists
    if await get_user_by_username(user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create user
    user_in_db = await create_user(user_create)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user_in_db.id), expires_delta=access_token_expires
    )
    
    # Convert UserInDB to User and add token
    return UserWithToken(
        **User.from_orm(user_in_db).dict(),
        access_token=access_token,
        token_type="bearer",
        following_count=0,
        followers_count=0
    )


@router.post("/refresh-token", response_model=Dict[str, str])
async def refresh_token(current_user: User = Depends(get_current_user)) -> Any:
    """
    Refresh access token.
    
    Args:
        current_user: Current user
        
    Returns:
        New access token
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(current_user.id), expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
