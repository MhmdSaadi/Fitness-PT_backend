from enum import Enum
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field 
from typing import List, Optional
from datetime import datetime, date
from sqlmodel import SQLModel

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    lightly_active = "lightly_active"
    moderately_active = "moderately_active"
    very_active = "very_active"
    extremely_active = "extremely_active"

class UserCreateModel(SQLModel): 
    """Schema for creating a new user account."""
    username: str = Field(max_length=50)
    email: EmailStr = Field(max_length=255)
    first_name: str
    last_name: str
    password: str = Field(min_length=6)
    
    # Optional fields for registration
    phone_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    height_cm: Optional[float] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    activity_level: Optional[ActivityLevel] = None
    medical_conditions: Optional[str] = None
    primary_concerns: Optional[str] = None
    fitness_goals: Optional[str] = None
    profile_picture_url: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "footfit_user",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "SecurePass123!",
                "phone_number": "+1234567890",
                "date_of_birth": "1990-01-01",
                "height_cm": 175.0,
                "weight_kg": 70.0,
                "activity_level": "moderately_active",
                "primary_concerns": "Flat feet and occasional heel pain",
                "fitness_goals": "Improve foot strength and reduce pain",
                "bio": "Looking to improve my foot health"
            }
        }
    }

class UserUpdateModel(SQLModel): 
    """Schema for updating existing user information."""
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=255)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    
    # Personal Information
    date_of_birth: Optional[date] = None
    height_cm: Optional[float] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    
    # Health Information
    activity_level: Optional[ActivityLevel] = None
    medical_conditions: Optional[str] = None
    medications: Optional[str] = None
    previous_injuries: Optional[str] = None
    
    # Foot Information
    shoe_size: Optional[str] = Field(None, max_length=10)
    foot_type: Optional[str] = None
    primary_concerns: Optional[str] = None
    pain_areas: Optional[str] = None
    
    # Goals
    fitness_goals: Optional[str] = None
    preferred_workout_time: Optional[str] = None
    exercise_experience: Optional[str] = None
    
    # Emergency Contact
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    
    profile_picture_url: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None)

class UserModel(SQLModel): 
    """Schema for representing a user in API responses."""
    uid: UUID
    username: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    phone_number: Optional[str]
    
    # Personal Information
    date_of_birth: Optional[date]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    
    # Health Information
    activity_level: Optional[ActivityLevel]
    medical_conditions: Optional[str]
    medications: Optional[str]
    previous_injuries: Optional[str]
    
    # Foot Information
    shoe_size: Optional[str]
    foot_type: Optional[str]
    primary_concerns: Optional[str]
    pain_areas: Optional[str]
    
    # Goals
    fitness_goals: Optional[str]
    preferred_workout_time: Optional[str]
    exercise_experience: Optional[str]
    
    # Emergency Contact
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relationship: Optional[str]
    
    profile_picture_url: Optional[str]
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_verified: bool

    class Config:
        from_attributes = True 

class UserLoginModel(SQLModel): 
    """Schema for user login credentials."""
    email: EmailStr = Field(max_length=255)
    password: str

class PasswordResetRequestModel(SQLModel): 
    """Schema for requesting a password reset."""
    email: EmailStr

class PasswordResetConfirmModel(SQLModel): 
    """Schema for confirming a password reset with new passwords."""
    new_password: str = Field(min_length=6)
    confirm_new_password: str = Field(min_length=6)