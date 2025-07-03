from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID, uuid4
from enum import Enum

class SessionStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"

class SessionType(str, Enum):
    personal = "personal"
    group = "group"
    virtual = "virtual"

class CoachingSession(SQLModel, table=True):
    __tablename__ = "coaching_sessions"
    
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    client_uid: UUID = Field(foreign_key="users.uid")
    title: str
    description: Optional[str] = None
    session_type: SessionType
    session_date: datetime
    duration_minutes: int = Field(default=60)
    status: SessionStatus = Field(default=SessionStatus.scheduled)
    notes: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ClientProgress(SQLModel, table=True):
    __tablename__ = "client_progress"
    
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    client_uid: UUID = Field(foreign_key="users.uid")
    session_uid: Optional[UUID] = Field(foreign_key="coaching_sessions.uid", default=None)
    date_recorded: date
    weight: Optional[float] = None
    pain_level: Optional[int] = Field(None, ge=0, le=10)  # 0-10 scale
    mobility_score: Optional[int] = Field(None, ge=0, le=10)  # 0-10 scale
    strength_score: Optional[int] = Field(None, ge=0, le=10)  # 0-10 scale
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Exercise(SQLModel, table=True):
    __tablename__ = "exercises"
    
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str
    instructions: str
    difficulty_level: int = Field(ge=1, le=5)  # 1-5 scale
    target_area: str  # e.g., "arch", "heel", "toes", "ankle"
    equipment_needed: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkoutPlan(SQLModel, table=True):
    __tablename__ = "workout_plans"
    
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    client_uid: UUID = Field(foreign_key="users.uid")
    name: str
    description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkoutPlanExercise(SQLModel, table=True):
    __tablename__ = "workout_plan_exercises"
    
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    workout_plan_uid: UUID = Field(foreign_key="workout_plans.uid")
    exercise_uid: UUID = Field(foreign_key="exercises.uid")
    sets: int = Field(default=1)
    reps: Optional[int] = None
    duration_seconds: Optional[int] = None
    rest_seconds: Optional[int] = Field(default=30)
    order_index: int = Field(default=0)
    notes: Optional[str] = None

class ClientAssessment(SQLModel, table=True):
    __tablename__ = "client_assessments"
    
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    client_uid: UUID = Field(foreign_key="users.uid")
    assessment_date: date
    foot_type: Optional[str] = None  # e.g., "flat", "high arch", "normal"
    gait_analysis: Optional[str] = None
    pain_areas: Optional[str] = None
    medical_history: Optional[str] = None
    goals: Optional[str] = None
    lifestyle_factors: Optional[str] = None
    current_activity_level: Optional[int] = Field(None, ge=1, le=5)  # 1-5 scale
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)