from uuid import uuid4

import aiofiles
from sqlalchemy import insert, select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from src.users.service import user_repo
from src.workouts.models import Exercise, Exercise_photo, Workout, Set, added_workouts_association, DifficultyWorkout
from src.workouts.schemas import WorkoutUpdate, ExerciseUpdate, SetUpdate


class WorkoutRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_workout(self, data):
        stat = insert(Workout).values(**data.model_dump()).returning(Workout.id)
        result = await self.session.execute(stat)
        workout_id = result.scalar()
        return workout_id

    async def update_workout(self, workout_id: int, data: WorkoutUpdate):
        query = update(Workout).filter(Workout.id == workout_id).values(**data.model_dump(exclude_none=True))
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundError("Workout not found")

        workout = await self.session.get(Workout, workout_id)
        return workout

    async def get_workouts(
            self,
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
        result = await self.session.execute(query)
        workouts = result.mappings().all()
        return workouts

    async def count_workouts(
            self,
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

        total = await self.session.scalar(query)
        return total

    async def get_user_workout_association(self, user_id, workout_id):
        stmt = select(added_workouts_association).where(
            (added_workouts_association.c.user_table == user_id) &
            (added_workouts_association.c.workout_table == workout_id)
        )
        return await self.session.execute(stmt)

    async def add_user_workout_association(self, user_id, workout_id):
        user = await user_repo.get_user_by_id(self.session, user_id)

        query_workout = select(Workout).filter(Workout.id == workout_id)
        result_workout = await self.session.execute(query_workout)
        workout = result_workout.first()

        if not user or not workout:
            return None

        new_association = insert(added_workouts_association).values(user_table=user_id, workout_table=workout_id)
        await self.session.execute(new_association)

        return True

    async def get_workout_by_id(self, workout_id: int):
        return await self.session.get(Workout, workout_id)

    async def get_one_workout(self, workout_id: int) -> Workout | None:
        query = select(Workout).filter(Workout.id == workout_id).options(
            selectinload(Workout.exercise).options(selectinload(Exercise.photo)))
        result = await self.session.execute(query)
        # mapping = result.mappings().one()
        mapping = result.mappings().first()
        workout = mapping["Workout"] if mapping else None
        return workout

    async def get_active_workout(self, workout_id: int, user_id: int):
        association_query = select(added_workouts_association).filter(
            added_workouts_association.c.workout_table == workout_id,
            added_workouts_association.c.user_table == user_id)

        association_query_result = await self.session.execute(association_query)
        return association_query_result

    async def get_user_added_workouts(
            self,
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
        result = await self.session.execute(query)
        user_workouts = result.mappings().all()
        return user_workouts

    async def count_user_added_workouts(
            self,
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
        return await self.session.scalar(query)

    async def get_workout_difficulties(self):
        query = select(DifficultyWorkout)
        result = await self.session.execute(query)
        workout_difficulties = result.mappings().all()
        return workout_difficulties

    async def get_exercises_by_workout_id(self, workout_id: int):
        query = await self.session.execute(select(Exercise).filter(Exercise.workout_id == workout_id))
        exercises = query.mappings().all()
        return exercises

    async def get_photos_exercise_by_id(self, exercise_id: int):
        photos_exercise = await self.session.execute(
            select(Exercise_photo).filter(Exercise_photo.exercise_id == exercise_id))
        result_photos_exercise = photos_exercise.mappings().all()
        return result_photos_exercise

    async def delete_created_workout_by_id(self, workout_id: int):
        query = delete(Workout).filter(Workout.id == workout_id)
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NotFoundError("Workout not found")

    async def delete_added_workout(self, user_id: int, workout_id: int) -> None:
        query = delete(added_workouts_association).where(
            (added_workouts_association.c.workout_table == workout_id) &
            (added_workouts_association.c.user_table == user_id)
        )
        result = await self.session.execute(query)
        if result.rowcount == 0:
            # Опционально: можно бросать NotFoundError, если пользователь не добавлял тренировку
            raise NotFoundError("Workout not found for this user")


class ExerciseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_exercise(self, data) -> int:
        stat = insert(Exercise).values(**data.model_dump(exclude_none=True)).returning(Exercise.id)
        result = await self.session.execute(stat)
        return result.scalar_one()

    async def get_exercise_by_id(self, exercise_id: int):
        return await self.session.get(Exercise, exercise_id)

    async def update_exercise(self, exercise_id: int, update_data: ExerciseUpdate):
        query = update(Exercise).where(Exercise.id == exercise_id).values(
            **update_data.model_dump(exclude_none=True))
        await self.session.execute(query)

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
        await self.session.execute(delete(Exercise).where(Exercise.id == exercise_id))

    async def delete_photos_by_ids(self, photo_ids: list[int]):
        await self.session.execute(delete(Exercise_photo).filter(Exercise_photo.id.in_(photo_ids)))


class SetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_set(self, number_sets: int, data: SetCreate):
        for _ in range(number_sets):
            stat = insert(Set).values(**data.model_dump())
            await self.session.execute(stat)

    async def get_sets(self, user_id: int, exercise_ids: list[int]):
        query = select(Set).filter(Set.exercise_id.in_(exercise_ids)).filter(Set.user_id == user_id).order_by(Set.id)
        result = await self.session.execute(query)
        sets = result.mappings().all()
        return sets

    async def update_set(self, set_id: int, update_data: SetUpdate):
        query = update(Set).filter(Set.id == set_id).values(**update_data.model_dump(exclude_none=True))
        await self.session.execute(query)

    async def delete_set(self, exercise_id: int, user_id: int):
        query = delete(Set).where((Set.exercise_id == exercise_id) and (Set.user_id == user_id))
        await self.session.execute(query)
