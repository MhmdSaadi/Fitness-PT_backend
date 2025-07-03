from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from sqlmodel import SQLModel
from .models import SessionStatus, SessionType

class CoachingSessionCreate(SQLModel):
    client_uid: UUID
    title: str
    description: Optional[str] = None
    session_type: SessionType
    session_date: datetime
    duration_minutes: int = Field(default=60)
    price: Optional[float] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None

class CoachingSessionUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    session_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[SessionStatus] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None

class CoachingSessionResponse(SQLModel):
    uid: UUID
    client_uid: UUID
    title: str
    description: Optional[str]
    session_type: SessionType
    session_date: datetime
    duration_minutes: int
    status: SessionStatus
    notes: Optional[str]
    price: Optional[float]
    location: Optional[str]
    meeting_link: Optional[str]
    created_at: datetime
    updated_at: datetime

class ClientProgressCreate(SQLModel):
    client_uid: UUID
    session_uid: Optional[UUID] = None
    date_recorded: date
    weight: Optional[float] = None
    pain_level: Optional[int] = Field(None, ge=0, le=10)
    mobility_score: Optional[int] = Field(None, ge=0, le=10)
    strength_score: Optional[int] = Field(None, ge=0, le=10)
    notes: Optional[str] = None

class ClientProgressResponse(SQLModel):
    uid: UUID
    client_uid: UUID
    session_uid: Optional[UUID]
    date_recorded: date
    weight: Optional[float]
    pain_level: Optional[int]
    mobility_score: Optional[int]
    strength_score: Optional[int]
    notes: Optional[str]
    created_at: datetime

class ExerciseCreate(SQLModel):
    name: str
    description: str
    instructions: str
    difficulty_level: int = Field(ge=1, le=5)
    target_area: str
    equipment_needed: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None

class ExerciseUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    target_area: Optional[str] = None
    equipment_needed: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None

class ExerciseResponse(SQLModel):
    uid: UUID
    name: str
    description: str
    instructions: str
    difficulty_level: int
    target_area: str
    equipment_needed: Optional[str]
    video_url: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime

class WorkoutPlanCreate(SQLModel):
    client_uid: UUID
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None

class WorkoutPlanResponse(SQLModel):
    uid: UUID
    client_uid: UUID
    name: str
    description: Optional[str]
    start_date: date
    end_date: Optional[date]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class WorkoutPlanExerciseCreate(SQLModel):
    exercise_uid: UUID
    sets: int = Field(default=1)
    reps: Optional[int] = None
    duration_seconds: Optional[int] = None
    rest_seconds: Optional[int] = Field(default=30)
    order_index: int = Field(default=0)
    notes: Optional[str] = None

class ClientAssessmentCreate(SQLModel):
    client_uid: UUID
    assessment_date: date
    foot_type: Optional[str] = None
    gait_analysis: Optional[str] = None
    pain_areas: Optional[str] = None
    medical_history: Optional[str] = None
    goals: Optional[str] = None
    lifestyle_factors: Optional[str] = None
    current_activity_level: Optional[int] = Field(None, ge=1, le=5)

class ClientAssessmentResponse(SQLModel):
    uid: UUID
    client_uid: UUID
    assessment_date: date
    foot_type: Optional[str]
    gait_analysis: Optional[str]
    pain_areas: Optional[str]
    medical_history: Optional[str]
    goals: Optional[str]
    lifestyle_factors: Optional[str]
    current_activity_level: Optional[int]
    created_at: datetime
    updated_at: datetime