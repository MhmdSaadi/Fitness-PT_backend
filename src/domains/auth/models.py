from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID, uuid4
from enum import Enum

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    lightly_active = "lightly_active"
    moderately_active = "moderately_active"
    very_active = "very_active"
    extremely_active = "extremely_active"

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=255, unique=True, index=True)
    first_name: str
    last_name: str
    password_hash: str
    role: UserRole = Field(default=UserRole.user)
    
    # Basic Profile Information
    profile_picture_url: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    
    # Personal Information for Coaching
    date_of_birth: Optional[date] = None
    height_cm: Optional[float] = Field(None, gt=0, description="Height in centimeters")
    weight_kg: Optional[float] = Field(None, gt=0, description="Weight in kilograms")
    
    # Health and Fitness Information
    activity_level: Optional[ActivityLevel] = None
    medical_conditions: Optional[str] = Field(None, description="Any medical conditions or injuries")
    medications: Optional[str] = Field(None, description="Current medications")
    previous_injuries: Optional[str] = Field(None, description="Previous foot/ankle injuries")
    
    # Foot-Specific Information
    shoe_size: Optional[str] = Field(None, max_length=10)
    foot_type: Optional[str] = Field(None, description="e.g., flat feet, high arch, normal")
    primary_concerns: Optional[str] = Field(None, description="Main foot health concerns")
    pain_areas: Optional[str] = Field(None, description="Areas of foot pain or discomfort")
    
    # Goals and Preferences
    fitness_goals: Optional[str] = Field(None, description="What they want to achieve")
    preferred_workout_time: Optional[str] = Field(None, description="Preferred time for workouts")
    exercise_experience: Optional[str] = Field(None, description="Experience with foot exercises")
    
    # Emergency Contact
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relationship: Optional[str] = Field(None, max_length=50)
    
    # System Fields
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)