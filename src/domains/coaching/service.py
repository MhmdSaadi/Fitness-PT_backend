from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, date
from uuid import UUID
from typing import List, Optional
from src.core.logger import get_logger
from .models import (
    CoachingSession, ClientProgress, Exercise, 
    WorkoutPlan, WorkoutPlanExercise, ClientAssessment
)
from .schemas import (
    CoachingSessionCreate, CoachingSessionUpdate,
    ClientProgressCreate, ExerciseCreate, ExerciseUpdate,
    WorkoutPlanCreate, WorkoutPlanExerciseCreate,
    ClientAssessmentCreate
)

logger = get_logger(__name__)

class CoachingService:
    
    # Coaching Sessions
    async def create_session(self, session_data: CoachingSessionCreate, session: AsyncSession) -> CoachingSession:
        logger.info(f"Creating coaching session for client: {session_data.client_uid}")
        
        new_session = CoachingSession(**session_data.model_dump())
        session.add(new_session)
        await session.commit()
        await session.refresh(new_session)
        
        logger.info(f"Coaching session created: {new_session.uid}")
        return new_session
    
    async def get_sessions_by_client(self, client_uid: UUID, db_session: AsyncSession) -> List[CoachingSession]:
        statement = select(CoachingSession).where(CoachingSession.client_uid == client_uid)
        result = await db_session.execute(statement)
        return result.scalars().all()
    
    async def get_session_by_uid(self, session_uid: UUID, db_session: AsyncSession) -> Optional[CoachingSession]:
        statement = select(CoachingSession).where(CoachingSession.uid == session_uid)
        result = await db_session.execute(statement)
        return result.scalars().first()
    
    async def update_session(self, session_uid: UUID, update_data: CoachingSessionUpdate, db_session: AsyncSession) -> Optional[CoachingSession]:
        coaching_session = await self.get_session_by_uid(session_uid, db_session)
        if not coaching_session:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(coaching_session, field, value)
        
        coaching_session.updated_at = datetime.utcnow()
        db_session.add(coaching_session)
        await db_session.commit()
        await db_session.refresh(coaching_session)
        
        return coaching_session
    
    # Client Progress
    async def create_progress_entry(self, progress_data: ClientProgressCreate, session: AsyncSession) -> ClientProgress:
        logger.info(f"Creating progress entry for client: {progress_data.client_uid}")
        
        new_progress = ClientProgress(**progress_data.model_dump())
        session.add(new_progress)
        await session.commit()
        await session.refresh(new_progress)
        
        return new_progress
    
    async def get_client_progress(self, client_uid: UUID, db_session: AsyncSession) -> List[ClientProgress]:
        statement = select(ClientProgress).where(ClientProgress.client_uid == client_uid).order_by(ClientProgress.date_recorded.desc())
        result = await db_session.execute(statement)
        return result.scalars().all()
    
    # Exercises
    async def create_exercise(self, exercise_data: ExerciseCreate, session: AsyncSession) -> Exercise:
        logger.info(f"Creating exercise: {exercise_data.name}")
        
        new_exercise = Exercise(**exercise_data.model_dump())
        session.add(new_exercise)
        await session.commit()
        await session.refresh(new_exercise)
        
        return new_exercise
    
    async def get_all_exercises(self, db_session: AsyncSession) -> List[Exercise]:
        statement = select(Exercise).order_by(Exercise.name)
        result = await db_session.execute(statement)
        return result.scalars().all()
    
    async def get_exercise_by_uid(self, exercise_uid: UUID, db_session: AsyncSession) -> Optional[Exercise]:
        statement = select(Exercise).where(Exercise.uid == exercise_uid)
        result = await db_session.execute(statement)
        return result.scalars().first()
    
    async def update_exercise(self, exercise_uid: UUID, update_data: ExerciseUpdate, db_session: AsyncSession) -> Optional[Exercise]:
        exercise = await self.get_exercise_by_uid(exercise_uid, db_session)
        if not exercise:
            return None
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(exercise, field, value)
        
        exercise.updated_at = datetime.utcnow()
        db_session.add(exercise)
        await db_session.commit()
        await db_session.refresh(exercise)
        
        return exercise
    
    # Workout Plans
    async def create_workout_plan(self, plan_data: WorkoutPlanCreate, session: AsyncSession) -> WorkoutPlan:
        logger.info(f"Creating workout plan for client: {plan_data.client_uid}")
        
        new_plan = WorkoutPlan(**plan_data.model_dump())
        session.add(new_plan)
        await session.commit()
        await session.refresh(new_plan)
        
        return new_plan
    
    async def get_client_workout_plans(self, client_uid: UUID, db_session: AsyncSession) -> List[WorkoutPlan]:
        statement = select(WorkoutPlan).where(WorkoutPlan.client_uid == client_uid).order_by(WorkoutPlan.created_at.desc())
        result = await db_session.execute(statement)
        return result.scalars().all()
    
    async def add_exercise_to_plan(self, plan_uid: UUID, exercise_data: WorkoutPlanExerciseCreate, session: AsyncSession) -> WorkoutPlanExercise:
        plan_exercise = WorkoutPlanExercise(
            workout_plan_uid=plan_uid,
            **exercise_data.model_dump()
        )
        session.add(plan_exercise)
        await session.commit()
        await session.refresh(plan_exercise)
        
        return plan_exercise
    
    # Client Assessments
    async def create_assessment(self, assessment_data: ClientAssessmentCreate, session: AsyncSession) -> ClientAssessment:
        logger.info(f"Creating assessment for client: {assessment_data.client_uid}")
        
        new_assessment = ClientAssessment(**assessment_data.model_dump())
        session.add(new_assessment)
        await session.commit()
        await session.refresh(new_assessment)
        
        return new_assessment
    
    async def get_client_assessments(self, client_uid: UUID, db_session: AsyncSession) -> List[ClientAssessment]:
        statement = select(ClientAssessment).where(ClientAssessment.client_uid == client_uid).order_by(ClientAssessment.assessment_date.desc())
        result = await db_session.execute(statement)
        return result.scalars().all()