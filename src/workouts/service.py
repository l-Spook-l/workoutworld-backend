import os

from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.workouts.models import Exercise
from src.workouts.repository import ExerciseRepository, WorkoutRepository, SetRepository
from src.workouts.schemas import WorkoutCreate, WorkoutUpdate, ExerciseUpdate, SetUpdate, SetCreate
from src.users.service import user_repo


class WorkoutService:
    def __init__(self, repo: WorkoutRepository):
        self.repo = repo

    async def create_workout(self, form: WorkoutCreate):
        try:
            workout_id = await self.repo.create_workout(form)
            await self.repo.session.commit()
            return workout_id
        except WorkoutCreateError:
            await self.repo.session.rollback()

    async def get_filtered_workouts(
            self,
            user_id: int | None = None,
            name: str | None = None,
            difficulty: list[str] | None = None,
            skip: int = 0,
            limit: int = 12,
            is_public: bool | None = None
    ):
        workouts = await self.repo.get_workouts(
            user_id=user_id,
            name=name,
            difficulty=difficulty,
            skip=skip,
            limit=limit,
            is_public=is_public
        )
        total_count = await self.repo.count_workouts(
            user_id=user_id,
            name=name,
            difficulty=difficulty,
            is_public=is_public
        )
        return workouts, total_count

    async def add_user_workout_association(self, user, user_id, workout_id):
        if user.id == user_id:
            raise HTTPException(status_code=400, detail="This workout cannot be added to the workout creator")

        result_existing = await self.repo.get_user_workout_association(user_id, workout_id)
        if result_existing.scalar():
            raise HTTPException(status_code=400, detail="This workout is already added to the user")

        association_created = await self.repo.add_user_workout_association(user_id, workout_id)
        if not association_created:
            raise HTTPException(status_code=404, detail="User or Workout not found")

        await self.repo.session.commit()

    async def get_one_workout(self, workout_id: int, user_id: int = None):
        workout = await self.repo.get_one_workout(workout_id)
        if not workout.is_public and user_id != workout.user_id:
            raise HTTPException(status_code=403)
        return workout

    async def get_active_workout(self, workout_id: int, user_id: int):
        workout = await self.get_one_workout(workout_id, user_id)
        association_query_result = await self.repo.get_active_workout(workout_id, user_id)
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
            user_id=user_id,
            name=name,
            difficulty=difficulty,
            skip=skip,
            limit=limit,
        )
        total_count = await self.repo.count_user_added_workouts(
            user_id=user_id,
            name=name,
            difficulty=difficulty
        )

        return workouts, total_count

    async def get_workout_difficulties(self):
        workout_difficulties = await self.repo.get_workout_difficulties()
        return workout_difficulties

    async def update_workout(
            self,
            workout_id: int,
            update_data: WorkoutUpdate
    ):
        await self.repo.update_workout(workout_id, update_data)
        await self.repo.session.commit()

    async def delete_created_workout(self, workout_id: int):
        workout = await self.repo.get_workout_by_id(workout_id)
        if not workout:
            raise HTTPException(status_code=404, detail="Workout not found")

        exercises = await self.repo.get_exercises_by_workout_id(workout_id)
        for exercise in exercises:
            result_photos_exercise = await self.repo.get_photos_exercise_by_id(exercise.Exercise.id)
            for photo in result_photos_exercise:
                photo_path = os.path.join(f'src/{photo.Exercise_photo.photo}')
                if os.path.exists(photo_path):
                    os.remove(photo_path)

        await self.repo.delete_created_workout_by_id(workout_id)
        await self.repo.session.commit()

    async def delete_added_workout(self, user_id: int, workout_id: int):
        workout = await self.repo.get_workout_by_id(workout_id)
        if not workout:
            raise HTTPException(status_code=404, detail="Workout not found")

        await self.repo.delete_added_workout(user_id=user_id, workout_id=workout_id)
        await self.repo.session.commit()


class ExerciseService:
    def __init__(self, repo: ExerciseRepository):
        self.repo = repo

    async def create_exercise(self, form, photos: list[UploadFile] | None = None) -> int:
        if form.video and (not form.video.startswith("<iframe") or not form.video.endswith("iframe>")):
            form.video = ""

        exercise_id = await self.repo.create_exercise(form)
        if photos:
            await self.repo.save_photos(exercise_id, form.name, photos)

        await self.repo.session.commit()
        return exercise_id

    async def add_new_photos_exercise(self, exercise_id: int, exercise_name: str, photos: list):
        exercise = await self.repo.session.get(Exercise, exercise_id)  # TODO - а тут ли оно должно быть?
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")
        if photos:
            await self.repo.save_photos(exercise_id, exercise_name, photos)
        await self.repo.session.commit()

    async def update_exercise(self, exercise_id: int, update_data: ExerciseUpdate):
        if update_data.video:
            if update_data.video[:7] != "<iframe" or update_data.video[-7:] != "iframe>":
                update_data.video = ""

        await self.repo.update_exercise(exercise_id, update_data)
        await self.repo.session.commit()

    async def delete_created_exercise(self, exercise_id: int):
        exercise = await self.repo.get_exercise_by_id(exercise_id=exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        result_photos_exercise = await self.repo.get_photos_exercise_by_id(exercise_id=exercise_id)
        for photo in result_photos_exercise:
            photo_path = os.path.join(f'src/{photo.Exercise_photo.photo}')
            if os.path.exists(photo_path):
                os.remove(photo_path)

        await self.repo.delete_created_exercise_by_id(exercise_id=exercise_id)
        await self.repo.session.commit()

    async def delete_photo(self, exercise_id: int, photo_ids: list[int]):
        exercise = await self.repo.get_exercise_by_id(exercise_id=exercise_id)
        if not exercise:
            raise HTTPException(status_code=404, detail="Exercise not found")

        photos = await self.repo.get_photos_by_ids(photo_ids=photo_ids)
        for photo in photos:
            photo_path = f"src/{photo["Exercise_photo"].photo}"
            if os.path.exists(photo_path):
                os.remove(photo_path)

        await self.repo.delete_photos_by_ids(photo_ids=photo_ids)
        await self.repo.session.commit()


class SetService:
    def __init__(self, repo: SetRepository):
        self.repo = repo

    async def create_set(self, number_sets: int, data: SetCreate):
        new_set = await self.repo.create_set(number_sets=number_sets, data=data)
        await self.repo.session.commit()
        return new_set

    async def get_sets(self, user_id: int, exercise_ids: list[int]):
        sets = await self.repo.get_sets(user_id=user_id, exercise_ids=exercise_ids)
        return sets

    async def update_set(self, set_id: int, data: SetUpdate):
        await self.repo.update_set(set_id=set_id, update_data=data)
        await self.repo.session.commit()

    async def delete_set(self, exercise_id: int, user_id: int):
        await self.repo.delete_set(exercise_id=exercise_id, user_id=user_id)
        await self.repo.session.commit()
