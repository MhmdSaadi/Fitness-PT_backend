from datetime import datetime, timedelta
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.database import get_session
from src.core.config import settings
from src.core.logger import get_logger
from src.core.errors import UserAlreadyExists, UserNotFound, InvalidCredentials
from .service import UserService
from .models import User
from .dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    RoleChecker,
    get_current_user,
    add_jti_to_blocklist,
)
from .schemas import (
    UserCreateModel,
    UserLoginModel,
    UserModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from .utils import (
    create_url_safe_token,
    decode_url_safe_token,
    create_access_token,
    verify_password,
    generate_passwd_hash,
    send_email,
    validate_password_strength,
)

logger = get_logger(__name__)

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])
REFRESH_TOKEN_EXPIRY = 2  # Days

limiter = Limiter(key_func=get_remote_address)

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def create_user_account(
    request: Request,
    user_data: UserCreateModel,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Register a new user with email verification."""
    logger.info(f"User signup request for email: {user_data.email}")
    
    if not validate_password_strength(user_data.password):
        logger.warning(f"Password strength validation failed for: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain uppercase, lowercase, numbers, and special characters"
        )
    
    if await user_service.user_exists(user_data.email, session):
        logger.warning(f"User already exists: {user_data.email}")
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)
    logger.info(f"User created successfully: {user_data.email}")
    
    token = create_url_safe_token({"email": user_data.email})
    verification_link = f"http://{settings.DOMAIN}/api/v1/auth/verify/{token}"
    
    html_content = f"""
    <h1>Welcome to {settings.APP_NAME}!</h1>
    <p>Please click <a href="{verification_link}">here</a> to verify your email address.</p>
    <p>This link will expire in 24 hours.</p>
    """
    logger.info(f"Adding email verification task for: {user_data.email}")
    bg_tasks.add_task(send_email, [user_data.email], f"Welcome to {settings.APP_NAME} - Verify Your Email", html_content)

    return {
        "message": "Account created! Please check your email for verification.",
        "user": new_user,
    }

@auth_router.post("/login")
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    login_data: UserLoginModel, 
    session: AsyncSession = Depends(get_session)
):
    """Authenticate user and return JWT tokens."""
    logger.info(f"Login attempt for user: {login_data.email}")
    
    user = await user_service.get_user_by_email(login_data.email, session)
    if not user or not verify_password(login_data.password, user.password_hash):
        logger.warning(f"Invalid login credentials for: {login_data.email}")
        raise InvalidCredentials()

    if not user.is_verified:
        logger.warning(f"Unverified user attempted login: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )

    logger.info(f"User authenticated successfully: {login_data.email}")
    
    access_token = create_access_token({
        "email": user.email,
        "user_uid": str(user.uid),
        "role": user.role,
    })
    
    refresh_token = create_access_token(
        {"email": user.email, "user_uid": str(user.uid)},
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
    )

    logger.info(f"Login successful for: {login_data.email}")
    return JSONResponse({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "email": user.email,
            "uid": str(user.uid),
            "role": user.role,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "is_verified": user.is_verified
        },
    })

@auth_router.get("/me")
@limiter.limit("30/minute")
async def get_current_user_profile(
    request: Request,
    user: User = Depends(get_current_user),
    _: bool = Depends(role_checker),
):
    """Get details of the currently authenticated user."""
    logger.info(f"Profile request for user: {user.email}")
    return user

@auth_router.post("/logout")
@limiter.limit("5/minute")
async def logout(
    request: Request,
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session)
):
    """Logout user and invalidate tokens."""
    try:
        jti = token_details.get("jti")
        user_data = token_details.get("user", {})
        user_email = user_data.get("email")
        
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
            
        await add_jti_to_blocklist(jti)
        logger.info(f"User logged out successfully: {user_email}")
        return JSONResponse(
            content={"message": "Logged out successfully"},
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )

@auth_router.post("/password-reset-request")
@limiter.limit("2/minute")
async def request_password_reset(
    request: Request,
    email_data: PasswordResetRequestModel,
    bg_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    """Initiate password reset process."""
    logger.info(f"Password reset request for: {email_data.email}")
    
    user = await user_service.get_user_by_email(email_data.email, session)
    if not user:
        logger.info(f"Password reset requested for non-existent email: {email_data.email}")
        return {"message": "If an account exists, password reset instructions have been sent"}
    
    token = create_url_safe_token({"email": email_data.email}, purpose="password-reset")
    reset_link = f"http://{settings.DOMAIN}/auth/reset-password?token={token}"
    
    html_content = f"""
    <h1>Password Reset Request</h1>
    <p>Click <a href="{reset_link}">here</a> to reset your password.</p>
    <p>This link will expire in 1 hour.</p>
    <p>If you didn't request this, please ignore this email.</p>
    """
    logger.info(f"Adding password reset email task for: {email_data.email}")
    bg_tasks.add_task(send_email, [email_data.email], "Password Reset Request", html_content)
    
    return {"message": "If an account exists, password reset instructions have been sent"}

@auth_router.get("/password-reset-confirm/{token}")
async def get_password_reset_form(
    token: str,
    session: AsyncSession = Depends(get_session),
):
    """Validate password reset token."""
    logger.info(f"Password reset form request received with token: {token[:20]}...")
    token_data = decode_url_safe_token(token, purpose="password-reset")
    if not token_data:
        logger.error(f"Invalid password reset token: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    email = token_data.get("email")
    user = await user_service.get_user_by_email(email, session)
    if not user:
        logger.error(f"User not found for email: {email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"Password reset form validated for user: {email}")
    return {"message": "Token is valid", "email": email}

@auth_router.post("/password-reset-confirm/{token}")
async def confirm_password_reset(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    """Complete password reset process."""
    logger.info(f"Password reset confirmation request received with token: {token[:20]}...")
    
    if passwords.new_password != passwords.confirm_new_password:
        logger.warning("Password reset failed: Passwords do not match")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    if not validate_password_strength(passwords.new_password):
        logger.warning("Password reset failed: Password too weak")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain uppercase, lowercase, numbers, and special characters"
        )

    token_data = decode_url_safe_token(token, purpose="password-reset")
    if not token_data:
        logger.error(f"Invalid password reset token: {token[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
        
    email = token_data.get("email")
    logger.info(f"Processing password reset for: {email}")
    
    user = await user_service.get_user_by_email(email, session)
    if not user:
        logger.warning(f"Password reset failed: User not found: {email}")
        raise UserNotFound()

    user.password_hash = generate_passwd_hash(passwords.new_password)
    user.updated_at = datetime.utcnow()
    session.add(user)
    await session.commit()

    logger.info(f"Password reset successful for: {email}")
    return {"message": "Password has been reset successfully"}

@auth_router.get("/verify/{token}")
@limiter.limit("5/minute")
async def verify_email(
    request: Request,
    token: str,
    session: AsyncSession = Depends(get_session)
):
    """Verify user's email using the token."""
    token_data = decode_url_safe_token(token)
    if not token_data:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
    
    email = token_data.get("email")
    user = await user_service.get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user.is_verified = True
    await session.commit()
    return {"message": "Email verified successfully."}

@auth_router.post("/refresh")
@limiter.limit("5/minute")
async def refresh_token(
    request: Request,
    token_details: dict = Depends(RefreshTokenBearer()),
    session: AsyncSession = Depends(get_session)
):
    """Refresh access token using refresh token."""
    logger.info(f"Token refresh request for user: {token_details['user']['email']}")
    
    user = await user_service.get_user_by_email(token_details["user"]["email"], session)
    if not user:
        logger.warning(f"Token refresh failed: User not found: {token_details['user']['email']}")
        raise UserNotFound()

    if not user.is_verified:
        logger.warning(f"Token refresh failed: Unverified user: {token_details['user']['email']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before using the service"
        )

    access_token = create_access_token({
        "email": user.email,
        "user_uid": str(user.uid),
        "role": user.role,
    })
    
    refresh_token = create_access_token(
        {"email": user.email, "user_uid": str(user.uid)},
        refresh=True,
        expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
    )

    logger.info(f"Token refresh successful for: {user.email}")
    return JSONResponse({
        "access_token": access_token,
        "refresh_token": refresh_token,
    })

@auth_router.post("/set-role/{user_email}", response_model=UserModel)
@limiter.limit("5/minute")
async def set_user_role(
    request: Request,
    user_email: str,
    role: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(RoleChecker(["admin"])),
):
    """Set a user's role (Admin only)."""
    logger.info(f"Admin {current_user.email} attempting to set role for {user_email} to {role}")
    
    if role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified. Role must be 'user' or 'admin'."
        )

    user_to_update = await user_service.get_user_by_email(user_email, session)
    if not user_to_update:
        logger.warning(f"Attempt to set role for non-existent user: {user_email}")
        raise UserNotFound()

    updated_user = await user_service.set_user_role(user_to_update, role, session)
    logger.info(f"Successfully set role for {user_email} to {role} by admin {current_user.email}")
    return updated_user