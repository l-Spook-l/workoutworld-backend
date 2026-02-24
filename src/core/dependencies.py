from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.workouts.repository import WorkoutRepository, ExerciseRepository, SetRepository
from src.workouts.service import WorkoutService, ExerciseService, SetService


def get_workout_service(session: AsyncSession = Depends(get_async_session)):
    repo = WorkoutRepository(session)
    return WorkoutService(repo)


def get_exercise_service(session: AsyncSession = Depends(get_async_session)):
    repo = ExerciseRepository(session)
    return ExerciseService(repo)


def get_set_service(session: AsyncSession = Depends(get_async_session)):
    repo = SetRepository(session)
    return SetService(repo)
