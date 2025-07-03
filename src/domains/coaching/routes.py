from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from uuid import UUID
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.database import get_session
from src.core.logger import get_logger
from src.domains.auth.dependencies import get_current_user, RoleChecker
from src.domains.auth.models import User
from .service import CoachingService
from .schemas import (
    CoachingSessionCreate, CoachingSessionUpdate, CoachingSessionResponse,
    ClientProgressCreate, ClientProgressResponse,
    ExerciseCreate, ExerciseUpdate, ExerciseResponse,
    WorkoutPlanCreate, WorkoutPlanResponse, WorkoutPlanExerciseCreate,
    ClientAssessmentCreate, ClientAssessmentResponse
)

logger = get_logger(__name__)

coaching_router = APIRouter()
coaching_service = CoachingService()
admin_role_checker = RoleChecker(["admin"])
limiter = Limiter(key_func=get_remote_address)

# Coaching Sessions
@coaching_router.post("/sessions", response_model=CoachingSessionResponse)
@limiter.limit("10/minute")
async def create_coaching_session(
    request: Request,
    session_data: CoachingSessionCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(admin_role_checker)
):
    """Create a new coaching session (Admin only)."""
    logger.info(f"Admin {current_user.email} creating session for client {session_data.client_uid}")
    
    new_session = await coaching_service.create_session(session_data, session)
    return new_session

@coaching_router.get("/sessions/client/{client_uid}", response_model=List[CoachingSessionResponse])
@limiter.limit("30/minute")
async def get_client_sessions(
    request: Request,
    client_uid: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all sessions for a specific client."""
    # Users can only see their own sessions, admins can see any
    if current_user.role != "admin" and str(current_user.uid) != str(client_uid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own sessions"
        )
    
    sessions = await coaching_service.get_sessions_by_client(client_uid, session)
    return sessions

@coaching_router.put("/sessions/{session_uid}", response_model=CoachingSessionResponse)
@limiter.limit("10/minute")
async def update_coaching_session(
    request: Request,
    session_uid: UUID,
    update_data: CoachingSessionUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(admin_role_checker)
):
    """Update a coaching session (Admin only)."""
    updated_session = await coaching_service.update_session(session_uid, update_data, session)
    if not updated_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return updated_session

# Client Progress
@coaching_router.post("/progress", response_model=ClientProgressResponse)
@limiter.limit("20/minute")
async def create_progress_entry(
    request: Request,
    progress_data: ClientProgressCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Create a progress entry."""
    # Users can only create progress for themselves, admins can create for anyone
    if current_user.role != "admin" and str(current_user.uid) != str(progress_data.client_uid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create progress entries for yourself"
        )
    
    progress = await coaching_service.create_progress_entry(progress_data, session)
    return progress

@coaching_router.get("/progress/client/{client_uid}", response_model=List[ClientProgressResponse])
@limiter.limit("30/minute")
async def get_client_progress(
    request: Request,
    client_uid: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get progress entries for a client."""
    # Users can only see their own progress, admins can see any
    if current_user.role != "admin" and str(current_user.uid) != str(client_uid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own progress"
        )
    
    progress = await coaching_service.get_client_progress(client_uid, session)
    return progress

# Exercises
@coaching_router.post("/exercises", response_model=ExerciseResponse)
@limiter.limit("10/minute")
async def create_exercise(
    request: Request,
    exercise_data: ExerciseCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(admin_role_checker)
):
    """Create a new exercise (Admin only)."""
    exercise = await coaching_service.create_exercise(exercise_data, session)
    return exercise

@coaching_router.get("/exercises", response_model=List[ExerciseResponse])
@limiter.limit("30/minute")
async def get_all_exercises(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get all exercises."""
    exercises = await coaching_service.get_all_exercises(session)
    return exercises

@coaching_router.put("/exercises/{exercise_uid}", response_model=ExerciseResponse)
@limiter.limit("10/minute")
async def update_exercise(
    request: Request,
    exercise_uid: UUID,
    update_data: ExerciseUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(admin_role_checker)
):
    """Update an exercise (Admin only)."""
    exercise = await coaching_service.update_exercise(exercise_uid, update_data, session)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    return exercise

# Workout Plans
@coaching_router.post("/workout-plans", response_model=WorkoutPlanResponse)
@limiter.limit("10/minute")
async def create_workout_plan(
    request: Request,
    plan_data: WorkoutPlanCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(admin_role_checker)
):
    """Create a workout plan (Admin only)."""
    plan = await coaching_service.create_workout_plan(plan_data, session)
    return plan

@coaching_router.get("/workout-plans/client/{client_uid}", response_model=List[WorkoutPlanResponse])
@limiter.limit("30/minute")
async def get_client_workout_plans(
    request: Request,
    client_uid: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get workout plans for a client."""
    # Users can only see their own plans, admins can see any
    if current_user.role != "admin" and str(current_user.uid) != str(client_uid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own workout plans"
        )
    
    plans = await coaching_service.get_client_workout_plans(client_uid, session)
    return plans

@coaching_router.post("/workout-plans/{plan_uid}/exercises")
@limiter.limit("20/minute")
async def add_exercise_to_plan(
    request: Request,
    plan_uid: UUID,
    exercise_data: WorkoutPlanExerciseCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(admin_role_checker)
):
    """Add an exercise to a workout plan (Admin only)."""
    plan_exercise = await coaching_service.add_exercise_to_plan(plan_uid, exercise_data, session)
    return {"message": "Exercise added to plan successfully", "uid": plan_exercise.uid}

# Client Assessments
@coaching_router.post("/assessments", response_model=ClientAssessmentResponse)
@limiter.limit("10/minute")
async def create_assessment(
    request: Request,
    assessment_data: ClientAssessmentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(admin_role_checker)
):
    """Create a client assessment (Admin only)."""
    assessment = await coaching_service.create_assessment(assessment_data, session)
    return assessment

@coaching_router.get("/assessments/client/{client_uid}", response_model=List[ClientAssessmentResponse])
@limiter.limit("30/minute")
async def get_client_assessments(
    request: Request,
    client_uid: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get assessments for a client."""
    # Users can only see their own assessments, admins can see any
    if current_user.role != "admin" and str(current_user.uid) != str(client_uid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own assessments"
        )
    
    assessments = await coaching_service.get_client_assessments(client_uid, session)
    return assessments