from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime
from uuid import UUID
from src.core.logger import get_logger
from .models import User, UserRole
from .schemas import UserCreateModel
from .utils import generate_passwd_hash

logger = get_logger(__name__)

class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        logger.debug(f"Attempting to fetch user by email: {email}")
        start_time = datetime.utcnow()
        
        try:
            statement = select(User).where(User.email == email)
            result = await session.execute(statement)
            user = result.scalars().first()
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            if user:
                logger.info(f"User found: {email} (took {duration:.3f}s)")
                logger.debug(f"User details - UID: {user.uid}, Role: {user.role}, Verified: {user.is_verified}")
            else:
                logger.info(f"User not found: {email} (took {duration:.3f}s)")
            
            return user
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error fetching user {email}: {str(e)} (took {duration:.3f}s)")
            raise

    async def get_user_by_uid(self, uid: UUID, session: AsyncSession) -> User | None:
        logger.debug(f"Attempting to fetch user by UID: {uid}")
        start_time = datetime.utcnow()
        
        try:
            statement = select(User).where(User.uid == uid)
            result = await session.execute(statement)
            user = result.scalars().first()
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            if user:
                logger.info(f"User found with UID: {uid} (took {duration:.3f}s)")
            else:
                logger.info(f"User not found with UID: {uid} (took {duration:.3f}s)")
            
            return user
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error fetching user with UID {uid}: {str(e)} (took {duration:.3f}s)")
            raise

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        logger.debug(f"Checking if user exists: {email}")
        start_time = datetime.utcnow()
        
        try:
            user = await self.get_user_by_email(email, session)
            exists = user is not None
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"User existence check for {email}: {exists} (took {duration:.3f}s)")
            return exists
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error checking user existence for {email}: {str(e)} (took {duration:.3f}s)")
            raise

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        logger.info(f"Starting user creation process for: {user_data.email}")
        start_time = datetime.utcnow()
        
        try:
            user_data_dict = user_data.model_dump()
            logger.debug(f"User data prepared for creation: {user_data.email}")
            
            new_user = User(**user_data_dict)
            new_user.password_hash = generate_passwd_hash(user_data_dict["password"])
            new_user.role = UserRole.user
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"User created successfully: {user_data.email} (took {duration:.3f}s)")
            logger.debug(f"New user details - ID: {new_user.uid}, Role: {new_user.role}")
            
            return new_user
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error creating user {user_data.email}: {str(e)} (took {duration:.3f}s)")
            raise

    async def set_user_role(self, user: User, role: str, session: AsyncSession) -> User:
        logger.info(f"Attempting to set role for user {user.email} to {role}")
        start_time = datetime.utcnow()
        try:
            user.role = UserRole(role)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"User {user.email} role set to {role} successfully (took {duration:.3f}s)")
            return user
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error setting role for user {user.email}: {str(e)} (took {duration:.3f}s)")
            raise

    async def update_user(self, user: User, user_data: dict, session: AsyncSession) -> User:
        logger.info(f"Starting user update process for: {user.email}")
        start_time = datetime.utcnow()
        
        try:
            changes = []
            for field, value in user_data.items():
                if field == "password":
                    new_hash = generate_passwd_hash(value)
                    if user.password_hash != new_hash:
                        changes.append("password: [updated]")
                        user.password_hash = new_hash
                elif hasattr(user, field):
                    old_value = getattr(user, field)
                    if old_value != value:
                        changes.append(f"{field}: {old_value} -> {value}")
                        setattr(user, field, value)
            
            if changes:
                logger.debug(f"User changes for {user.email}: {', '.join(changes)}")
                user.updated_at = datetime.utcnow()
                session.add(user)
                await session.commit()
                await session.refresh(user)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"User updated successfully: {user.email} (took {duration:.3f}s)")
            
            return user
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error updating user {user.email}: {str(e)} (took {duration:.3f}s)")
            raise