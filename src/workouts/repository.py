from uuid import uuid4

import aiofiles
from sqlalchemy import insert, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.workouts.models import Exercise, Exercise_photo, Workout, Set, added_workouts_association


class WorkoutRepository:
    async def create_workout(self, session, data):
        stat = insert(Workout).values(**data.model_dump()).returning(Workout.id)
        result = await session.execute(stat)
        workout_id = result.scalar()
        return workout_id

    @staticmethod
    async def get_workouts(session,
                           name: str | None = None,
                           difficulty: list[str] | None = None,
                           skip: int = 0,
                           limit: int = 12
                           ):
        query = select(Workout).filter(Workout.is_public)
        if name:
            query = query.filter(Workout.name.ilike(f"%{name}%"))
        if difficulty:
            query = query.filter(Workout.difficulty.in_(difficulty))
        query = query.limit(limit).offset(skip)
        result = await session.execute(query)
        workouts = result.mappings().all()
        return workouts

    @staticmethod
    async def count_workouts(session: AsyncSession,
                             name: str | None = None,
                             difficulty: list[str] | None = None,
                             ):
        query = select(func.count()).select_from(Workout).filter(Workout.is_public)
        if name:
            query = query.filter(Workout.name.ilike(f"%{name}%"))
        if difficulty:
            query = query.filter(Workout.difficulty.in_(difficulty))

        total = await session.scalar(query)
        return total

    async def get_user_workout_association(self, session, user_id, workout_id):
        stmt = select(added_workouts_association).where(
            (added_workouts_association.c.user_table == user_id) &
            (added_workouts_association.c.workout_table == workout_id)
        )
        return await session.execute(stmt)

    async def add_user_workout_association(self, session, user_id, workout_id):
        query_user = select(User).filter(User.id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.first()

        query_workout = select(Workout).filter(Workout.id == workout_id)
        result_workout = await session.execute(query_workout)
        workout = result_workout.first()

        if not user or not workout:
            return None

        new_association = insert(added_workouts_association).values(user_table=user_id, workout_table=workout_id)
        await session.execute(new_association)

        return True


class ExerciseRepository:
    async def create_exercise(self, session, data):
        stat = insert(Exercise).values(**data.model_dump(exclude_none=True)).returning(Exercise.id)
        result = await session.execute(stat)
        exercise_id = result.scalar()
        return exercise_id

    async def save_photos(self, session, exercise_id: int, exercise_name: str, photos: list):
        for photo in photos:
            photo.filename = photo.filename.lower()
            path_photo = f"src/media/Photos_exercise/{exercise_id}_{exercise_name}_{uuid4()}.png"
            async with aiofiles.open(path_photo, "+wb") as buffer:
                data = await photo.read()
                await buffer.write(data)
            add_photo = insert(Exercise_photo).values(photo=path_photo[4:], exercise_id=exercise_id)
            await session.execute(add_photo)


class SetRepository:
    async def create_set(self, session, number_sets: int, data):
        for _ in range(number_sets):
            stat = insert(Set).values(**data.model_dump())
            await session.execute(stat)
