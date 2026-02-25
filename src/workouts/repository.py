from uuid import uuid4

import aiofiles
from sqlalchemy import insert, select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.users.service import user_repo
from src.workouts.models import Exercise, Exercise_photo, Workout, Set, added_workouts_association, DifficultyWorkout
from src.workouts.schemas import WorkoutUpdate, ExerciseUpdate, SetUpdate


class WorkoutRepository:
    @staticmethod
    async def create_workout(session: AsyncSession, data):
        stat = insert(Workout).values(**data.model_dump()).returning(Workout.id)
        result = await session.execute(stat)
        workout_id = result.scalar()
        return workout_id

    @staticmethod
    async def update_workout(session: AsyncSession, workout_id: int, data: WorkoutUpdate):
        query = update(Workout).filter(Workout.id == workout_id).values(**data.model_dump(exclude_none=True))
        await session.execute(query)

    @staticmethod
    async def get_workouts(
            session: AsyncSession,
            user_id: int | None = None,
            name: str | None = None,
            difficulty: list[str] | None = None,
            skip: int = 0,
            limit: int = 12,
            is_public: bool | None = None
    ):
        query = select(Workout)
        if user_id:
            query = query.filter(Workout.user_id == user_id)
        if name:
            query = query.filter(Workout.name.ilike(f"%{name}%"))
        if difficulty:
            query = query.filter(Workout.difficulty.in_(difficulty))
        if is_public is not None:
            query = query.filter(Workout.is_public == is_public)
        query = query.limit(limit).offset(skip)
        result = await session.execute(query)
        workouts = result.mappings().all()
        return workouts

    @staticmethod
    async def count_workouts(
            session: AsyncSession,
            user_id: int | None = None,
            name: str | None = None,
            difficulty: list[str] | None = None,
            is_public: bool | None = None
    ):
        query = select(func.count()).select_from(Workout)
        if user_id:  # TODO - user_id is not None, for 0 id
            query = query.filter(Workout.user_id == user_id)
        if name:
            query = query.filter(Workout.name.ilike(f"%{name}%"))
        if difficulty:
            query = query.filter(Workout.difficulty.in_(difficulty))
        if is_public is not None:
            query = query.filter(Workout.is_public == is_public)

        total = await session.scalar(query)
        return total

    @staticmethod
    async def get_user_workout_association(session: AsyncSession, user_id, workout_id):
        stmt = select(added_workouts_association).where(
            (added_workouts_association.c.user_table == user_id) &
            (added_workouts_association.c.workout_table == workout_id)
        )
        return await session.execute(stmt)

    @staticmethod
    async def add_user_workout_association(session: AsyncSession, user_id, workout_id):
        user = await user_repo.get_user_by_id(session, user_id)

        query_workout = select(Workout).filter(Workout.id == workout_id)
        result_workout = await session.execute(query_workout)
        workout = result_workout.first()

        if not user or not workout:
            return None

        new_association = insert(added_workouts_association).values(user_table=user_id, workout_table=workout_id)
        await session.execute(new_association)

        return True

    @staticmethod
    async def get_workout_by_id(session: AsyncSession, workout_id: int):
        return await session.get(Workout, workout_id)

    @staticmethod
    async def get_one_workout(session: AsyncSession, workout_id: int) -> Workout | None:
        query = select(Workout).filter(Workout.id == workout_id).options(
            selectinload(Workout.exercise).options(selectinload(Exercise.photo)))
        result = await session.execute(query)
        # mapping = result.mappings().one()
        mapping = result.mappings().first()
        workout = mapping["Workout"] if mapping else None
        return workout

    @staticmethod
    async def get_active_workout(session: AsyncSession, workout_id: int, user_id: int):
        association_query = select(added_workouts_association).filter(
            added_workouts_association.c.workout_table == workout_id,
            added_workouts_association.c.user_table == user_id)

        association_query_result = await session.execute(association_query)
        return association_query_result

    @staticmethod
    async def get_user_added_workouts(
            session: AsyncSession,
            user_id: int | None = None,
            name: str | None = None,
            difficulty: list[str] | None = None,
            skip: int = 0,
            limit: int = 12,
    ):
        query = select(Workout)
        query = query.join(added_workouts_association).filter(added_workouts_association.c.user_table == user_id)

        if name:
            query = query.filter(Workout.name.ilike(f"%{name}%"))
        if difficulty:
            query = query.filter(Workout.difficulty.in_(difficulty))

        query = query.limit(limit).offset(skip)
        result = await session.execute(query)
        user_workouts = result.mappings().all()
        return user_workouts

    @staticmethod
    async def count_user_added_workouts(
            session: AsyncSession,
            user_id: int,
            name: str | None = None,
            difficulty: list[str] | None = None
    ):
        query = (
            select(func.count())
            .select_from(Workout)
            .join(added_workouts_association)
            .filter(added_workouts_association.c.user_table == user_id)
        )
        if name:
            query = query.filter(Workout.name.ilike(f"%{name}%"))
        if difficulty:
            query = query.filter(Workout.difficulty.in_(difficulty))
        return await session.scalar(query)

    @staticmethod
    async def get_workout_difficulties(session: AsyncSession):
        query = select(DifficultyWorkout)
        result = await session.execute(query)
        workout_difficulties = result.mappings().all()
        return workout_difficulties

    @staticmethod
    async def delete_created_workout_by_id(session: AsyncSession, workout_id: int):
        query = delete(Workout).filter(Workout.id == workout_id)
        await session.execute(query)

    @staticmethod
    async def delete_added_workout(session: AsyncSession, user_id: int, workout_id: int):
        query = delete(added_workouts_association).where(
            (added_workouts_association.c.workout_table == workout_id) and
            (added_workouts_association.c.user_table == user_id)
        )
        await session.execute(query)


class ExerciseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_exercise(self, data) -> int:
        try:
            stat = insert(Exercise).values(**data.model_dump(exclude_none=True)).returning(Exercise.id)
            result = await self.session.execute(stat)
            exercise_id = result.scalar()
            return exercise_id
        except IntegrityError as exc:
            log.exception(exc)

    async def get_exercise_by_id(self, exercise_id: int):
        return await self.session.get(Exercise, exercise_id)

    async def update_exercise(self, exercise_id: int, update_data: ExerciseUpdate):
        try:
            query = update(Exercise).filter(Exercise.id == exercise_id).values(
                **update_data.model_dump(exclude_none=True))
            await self.session.execute(query)
        except IntegrityError as exc:
            log.exception(exc)

    async def get_exercises_by_workout_id(self, workout_id: int):
        query = await self.session.execute(select(Exercise).filter(Exercise.workout_id == workout_id))
        exercises = query.mappings().all()
        return exercises

    async def get_photos_exercise_by_id(self, exercise_id: int):
        photos_exercise = await self.session.execute(
            select(Exercise_photo).filter(Exercise_photo.exercise_id == exercise_id))
        result_photos_exercise = photos_exercise.mappings().all()
        return result_photos_exercise

    async def get_photos_by_ids(self, photo_ids: list[int]):
        query = select(Exercise_photo).filter(Exercise_photo.id.in_(photo_ids))
        result = await self.session.execute(query)
        photos = result.mappings().all()
        return photos

    # TODO перенести в слов сервиса т.к. это работа с файловой системой
    async def save_photos(self, exercise_id: int, exercise_name: str, photos: list):
        for photo in photos:
            photo.filename = photo.filename.lower()
            path_photo = f"src/media/Photos_exercise/{exercise_id}_{exercise_name}_{uuid4()}.png"
            async with aiofiles.open(path_photo, "+wb") as buffer:
                data = await photo.read()
                await buffer.write(data)
            add_photo = insert(Exercise_photo).values(photo=path_photo[4:], exercise_id=exercise_id)
            await self.session.execute(add_photo)

    async def delete_created_exercise_by_id(self, exercise_id: int):
        try:
            await self.session.execute(delete(Exercise).filter(Exercise.id == exercise_id))
        except IntegrityError as exc:
            log.exception(exc)

    async def delete_photos_by_ids(self, photo_ids: list[int]):
        try:
            await self.session.execute(delete(Exercise_photo).filter(Exercise_photo.id.in_(photo_ids)))
        except IntegrityError as exc:
            log.exception(exc)


class SetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_set(self, number_sets: int, data: SetCreate):
        try:
            for _ in range(number_sets):
                stat = insert(Set).values(**data.model_dump())
                await self.session.execute(stat)
        except IntegrityError as exc:
            log.exception(exc)

    async def get_sets(self, user_id: int, exercise_ids: list[int]):
        query = select(Set).filter(Set.exercise_id.in_(exercise_ids)).filter(Set.user_id == user_id).order_by(Set.id)
        result = await self.session.execute(query)
        sets = result.mappings().all()
        return sets

    async def update_set(self, set_id: int, update_data: SetUpdate):
        try:
            query = update(Set).filter(Set.id == set_id).values(**update_data.model_dump(exclude_none=True))
            await self.session.execute(query)
        except IntegrityError as exc:
            log.exception(exc)

    async def delete_set(self, exercise_id: int, user_id: int):
        query = delete(Set).where((Set.exercise_id == exercise_id) and (Set.user_id == user_id))
        await self.session.execute(query)
