from fastapi import UploadFile, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from src.workouts.models import Exercise, Workout
from src.workouts.repository import ExerciseRepository, WorkoutRepository, SetRepository
from src.workouts.schemas import WorkoutCreate


class WorkoutService:
    def __init__(self, repo: WorkoutRepository):
        self.repo = repo

    async def create_workout(self, session: AsyncSession, form: WorkoutCreate):
        workout_id = await self.repo.create_workout(session, form)
        await session.commit()
        return workout_id

    async def get_filtered_workouts(self,
                                    session,
                                    name: str | None = None,
                                    difficulty: list[str] | None = None,
                                    skip: int = 0,
                                    limit: int = 12
                                    ):
        workouts = await self.repo.get_workouts(
            session=session,
            name=name,
            difficulty=difficulty,
            skip=skip,
            limit=limit,
        )
        total_count = await self.repo.count_workouts(
            session=session,
            name=name,
            difficulty=difficulty,
        )
        return workouts, total_count

    async def add_user_workout_association(self, session, user, user_id, workout_id):
        if user.id == user_id:
            raise HTTPException(status_code=400, detail="This workout cannot be added to the workout creator")

        result_existing = await self.repo.get_user_workout_association(session, user_id, workout_id)
        if result_existing.scalar():
            raise HTTPException(status_code=400, detail="This workout is already added to the user")

        association_created = await self.repo.add_user_workout_association(session, user_id, workout_id)
        if not association_created:
            raise HTTPException(status_code=404, detail="User or Workout not found")

        await session.commit()

    async def get_one_workout(self, session: AsyncSession, workout_id: int, user_id: int = None):
        workout = await self.repo.get_one_workout(session, workout_id)
        if not workout.is_public and user_id != workout.user_id:
            raise HTTPException(status_code=403)
        return workout

    async def get_active_workout(self, session: AsyncSession, workout_id: int, user_id: int):
        workout = await self.get_one_workout(session, workout_id, user_id)
        association_query_result = await self.repo.get_active_workout(session, workout_id, user_id)
        if not association_query_result.first() and workout.user_id != user_id:
            raise HTTPException(status_code=403)
        return workout

    async def get_user_added_workouts(
            self,
            session: AsyncSession,
            user_id: int | None = None,
            name: str | None = None,
            difficulty: list[str] | None = None,
            skip: int = 0,
            limit: int = 12,
    ):
        user = await user_repo.get_user_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        workouts = await self.repo.get_user_added_workouts(
            session=session,
            user_id=user_id,
            name=name,
            difficulty=difficulty,
            skip=skip,
            limit=limit,
        )
        total_count = await self.repo.count_user_added_workouts(
            session=session,
            user_id=user_id,
            name=name,
            difficulty=difficulty
        )

        return workouts, total_count

    async def get_workout_difficulties(self, session: AsyncSession):
        workout_difficulties = await self.repo.get_workout_difficulties(session)
        return workout_difficulties


class ExerciseService:
    def __init__(self, repo: ExerciseRepository):
        self.repo = repo

    async def create_exercise(self, session: AsyncSession, form, photos: list[UploadFile] | None = None):
        if form.video and (not form.video.startswith("<iframe") or not form.video.endswith("iframe>")):
            form.video = ""

        exercise_id = await self.repo.create_exercise(session, form)

        if photos:
            await self.repo.save_photos(session, exercise_id, form.name, photos)

        await session.commit()
        return exercise_id

    async def add_new_photos_exercise(self, session, exercise_id: int, exercise_name: str, photos: list):
        exercise = await session.get(Exercise, exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        if photos:
            await self.repo.save_photos(session, exercise_id, exercise_name, photos)
        await session.commit()


class SetService:
    def __init__(self, repo: SetRepository):
        self.repo = repo

    async def create_set(self, session: AsyncSession, number_sets: int, data):
        await self.repo.create_set(session, number_sets, data)
        await session.commit()


workout_repo = WorkoutRepository()
exercise_repo = ExerciseRepository()
set_repo = SetRepository()

workout_service = WorkoutService(workout_repo)
exercise_service = ExerciseService(exercise_repo)
set_service = SetService(set_repo)
