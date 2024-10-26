import os
import aiofiles
from uuid import uuid4
from pydantic import ValidationError
from fastapi import APIRouter, Depends, Query, UploadFile, Form
from fastapi.exceptions import HTTPException
from sqlalchemy import select, insert, update, func, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound
from src.users.base_config import current_user
from src.core.database import get_async_session
from src.users.models import User
from .models import Workout, Exercise, Set, added_workouts_association, Exercise_photo, DifficultyWorkout
from .schemas import WorkoutCreate, ExerciseCreate, SetCreate, WorkoutUpdate, ExerciseUpdate, SetUpdate

router = APIRouter(
    prefix="/workouts",
    tags=["workouts"]
)


@router.post("/create_workout")
async def add_workout(new_workout: WorkoutCreate, user: User = Depends(current_user),
                      session: AsyncSession = Depends(get_async_session)):
    try:
        stat = insert(Workout).values(**new_workout.model_dump()).returning(Workout.id)
        result = await session.execute(stat)
        workout_id = result.scalar()
        await session.commit()
        return {"status": "success", "workout_ID": workout_id}
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.post("/create_exercise")
async def add_video_exercise(
        name: str = Form(...),
        workout_id: int = Form(...),
        description: str = Form(...),
        number_of_sets: int = Form(...),
        maximum_repetitions: int = Form(...),
        rest_time: int = Form(...),
        video: str = Form(None),
        photos: list[UploadFile] = None,
        number_in_workout: int = Form(...),
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)):
    if video:
        if video[:7] != "<iframe" or video[-7:] != "iframe>":
            video = ""

    try:
        exercise_data = ExerciseCreate(
            name=name,
            workout_id=workout_id,
            description=description,
            number_of_sets=number_of_sets,
            maximum_repetitions=maximum_repetitions,
            rest_time=rest_time,
            video=video,
            number_in_workout=number_in_workout,
        )

        stat = insert(Exercise).values(**exercise_data.model_dump(exclude_none=True)).returning(Exercise.id)
        result = await session.execute(stat)
        exercise_id = result.scalar()

        if photos:
            for photo in photos:
                photo.filename = photo.filename.lower()
                path_photos = f"src/media/Photos_exercise/{exercise_id}_{name}_{uuid4()}.png"
                async with aiofiles.open(path_photos, "+wb") as buffer:
                    data = await photo.read()
                    await buffer.write(data)
                add_photos = insert(Exercise_photo).values(photo=path_photos[4:], exercise_id=exercise_id)
                await session.execute(add_photos)

        await session.commit()
        return {"status": "success", "exercise_ID": exercise_id}
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = error['loc'][0]
            msg = error['msg']
            error_messages.append(f"Error in field '{field}': {msg}")
        raise HTTPException(status_code=422, detail=error_messages)


@router.post("/create_set")
async def add_set(number_sets: int, new_set: SetCreate, user: User = Depends(current_user),
                  session: AsyncSession = Depends(get_async_session)):
    try:
        for _ in range(number_sets):
            stat = insert(Set).values(**new_set.model_dump())
            await session.execute(stat)
        await session.commit()
        return {"status": "success"}
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.post("/add-workout-to-user/{user_id}/{workout_id}")
async def add_workout_to_user(user_id: int, workout_id: int, user: User = Depends(current_user),
                              session: AsyncSession = Depends(get_async_session)):
    existing_association = select(added_workouts_association).where(
        (added_workouts_association.c.user_table == user_id) &
        (added_workouts_association.c.workout_table == workout_id)
    )
    result_existing = await session.execute(existing_association)

    if user.id == user_id:
        raise HTTPException(status_code=400, detail="This workout cannot be added to the workout creator")

    if result_existing.scalar():
        raise HTTPException(status_code=400, detail="This workout is already added to the user")

    try:
        query_user = select(User).filter(User.id == user_id)
        result_user = await session.execute(query_user)
        user = result_user.first()

        query_workout = select(Workout).filter(Workout.id == workout_id)
        result_workout = await session.execute(query_workout)
        workout = result_workout.first()

        if not user or not workout:
            raise HTTPException(status_code=404, detail="User or Workout not found")

        new_association = insert(added_workouts_association).values(user_table=user_id, workout_table=workout_id)
        await session.execute(new_association)
        await session.commit()

        return {"status": "success", "message": "Workout added to user"}
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.post("/add-new-photos")
async def add_video_exercise(
        exercise_id: int,
        exercise_name: str,
        photos: list[UploadFile] = None,
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)):
    exercise = await session.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    try:
        if photos:
            for photo in photos:
                photo.filename = photo.filename.lower()
                path_photos = f"src/media/Photos_exercise/{exercise_id}_{exercise_name}_{uuid4()}.png"
                async with aiofiles.open(path_photos, "+wb") as buffer:
                    data = await photo.read()
                    await buffer.write(data)
                add_photos = insert(Exercise_photo).values(photo=path_photos[4:], exercise_id=exercise_id)
                await session.execute(add_photos)

        await session.commit()
        return {"status": "success", "exercise_ID": exercise_id}
    except ValidationError as e:

        raise HTTPException(status_code=422, detail=e)


@router.get("/")
async def get_workouts(
        name: str = Query(None, description="Filter by name"),
        difficulty: list[str] = Query(None, description="Filter by difficulty"),
        skip: int = Query(0, description="Number of records to skip"),
        limit: int = Query(12, description="Number of records to return"),
        page: int = Query(1, description="Page number"),
        session: AsyncSession = Depends(get_async_session)):
    # Normalizing the query for security (preventing SQL injections)
    query_name = f"%{name}%"

    try:
        query = select(Workout)
        if name:
            query = query.filter(Workout.name.ilike(query_name))
        if difficulty:
            query = query.filter(Workout.difficulty.in_(difficulty))

        query = query.limit(limit).offset(skip).filter(Workout.is_public)
        result = await session.execute(query)
        total_count = await session.scalar(
            select(func.count())
            .select_from(Workout)
            .filter(Workout.is_public)
            .filter(Workout.name.ilike(query_name) if name else True)
            .filter(Workout.difficulty.in_(difficulty) if difficulty else True)
        )
        workouts = result.mappings().all()

        return {
            "status": "success",
            "data": workouts,
            "skip": skip,
            "limit": limit,
            "total_count": total_count,
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.get("/workout/{workout_id}")
async def get_one_workout(workout_id: int, user_id: int = None, session: AsyncSession = Depends(get_async_session)):
    query = (select(Workout).filter(Workout.id == workout_id).
             options(selectinload(Workout.exercise).options(selectinload(Exercise.photo))))
    try:
        result = await session.execute(query)
        workout = workout_check = result.mappings().one()
        if not workout_check.Workout.is_public and user_id != workout_check.Workout.user_id:
            raise HTTPException(status_code=403)

        return {
            "status": "success",
            "data": workout,
            "details": None,
        }

    except NoResultFound:
        raise HTTPException(status_code=404, detail="This workout not found")
    except HTTPException as http_error:
        if http_error.status_code == 403:
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error")


@router.get("/active-workout")
async def get_one_workout(workout_id: int, user_id: int,
                          user: User = Depends(current_user),
                          session: AsyncSession = Depends(get_async_session)):
    query = (select(Workout).filter(Workout.id == workout_id).
             options(selectinload(Workout.exercise).options(selectinload(Exercise.photo))))
    try:
        result = await session.execute(query)
        workout = workout_check = result.mappings().one()

        association_query = (select(added_workouts_association)
                             .filter(added_workouts_association.c.workout_table == workout_id,
                                     added_workouts_association.c.user_table == user_id))
        association_query_result = await session.execute(association_query)

        if not workout_check.Workout.is_public and user_id != workout_check.Workout.user_id:
            raise HTTPException(status_code=403)

        if not association_query_result.first() and workout_check.Workout.user_id != user_id:
            raise HTTPException(status_code=403)

        return {
            "status": "success",
            "data": workout,
            "details": None,
        }

    except NoResultFound:
        raise HTTPException(status_code=404, detail="This workout not found")
    except HTTPException as http_error:
        if http_error.status_code == 403:
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server error")


@router.get("/user-workouts")
async def get_my_workouts(user_id: int,
                          name: str = Query(None, description="Filter by name"),
                          difficulty: list[str] = Query(None, description="Filter by difficulty"),
                          skip: int = Query(0, description="Number of records to skip"),
                          limit: int = Query(9, description="Number of records to return"),
                          is_public: bool = Query(None, description="Filter by status"),
                          page: int = Query(1, description="Page number"),
                          user: User = Depends(current_user),
                          session: AsyncSession = Depends(get_async_session)):
    query_name = f"%{name}%"

    try:
        query = select(Workout)

        if name:
            query = query.filter(Workout.name.ilike(query_name))
        if difficulty:
            query = query.filter(Workout.difficulty.in_(difficulty))
        if is_public is not None:
            query = query.filter(Workout.is_public == is_public)

        query = query.filter(Workout.user_id == user_id).limit(limit).offset(skip)
        result = await session.execute(query)
        my_workouts = result.mappings().all()
        total_count = await session.scalar(
            select(func.count())
            .select_from(Workout)
            .filter(Workout.user_id == user_id)
            .filter(Workout.name.ilike(query_name) if name else True)
            .filter(Workout.difficulty.in_(difficulty) if difficulty else True)
            .filter(Workout.is_public == is_public if is_public is not None else True)
        )

        return {
            "status": "success",
            "data": my_workouts,
            "skip": skip,
            "limit": limit,
            "total_count": total_count,
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.get("/get-user-added-workouts/{user_id}")
async def get_user_workouts(user_id: int,
                            name: str = Query(None, description="Filter by name"),
                            difficulty: list[str] = Query(None, description="Filter by difficulty"),
                            skip: int = Query(0, description="Number of records to skip"),
                            limit: int = Query(9, description="Number of records to return"),
                            page: int = Query(1, description="Page number"),
                            user: User = Depends(current_user),
                            session: AsyncSession = Depends(get_async_session)):
    query_user = select(User).filter(User.id == user_id)
    result_user = await session.execute(query_user)
    user = result_user.first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query_name = f"%{name}%"

    try:
        query = select(Workout)
        query = query.join(added_workouts_association).filter(added_workouts_association.c.user_table == user_id)

        if name:
            query = query.filter(Workout.name.ilike(query_name))
        if difficulty:
            query = query.filter(Workout.difficulty.in_(difficulty))

        query = query.limit(limit).offset(skip)
        result = await session.execute(query)
        user_workouts = result.mappings().all()

        total_count = await session.scalar(
            select(func.count())
            .select_from(Workout).join(added_workouts_association)
            .filter(added_workouts_association.c.user_table == user_id)
            .filter(Workout.name.ilike(query_name) if name else True)
            .filter(Workout.difficulty.in_(difficulty) if difficulty else True)
        )

        return {
            "status": "success",
            "user_id": user_id,
            "data": user_workouts,
            "skip": skip,
            "limit": limit,
            "total_count": total_count,
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.get("/workout-difficulties")
async def get_difficulty(session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(DifficultyWorkout)
        result = await session.execute(query)
        difficulty = result.mappings().all()
        return {
            "status": "success",
            "data": difficulty,
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.get("/sets")
async def get_sets(user_id: int, exercise_ids: list[int] = Query(None),
                   user: User = Depends(current_user),
                   session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Set).filter(Set.exercise_id.in_(exercise_ids)).filter(Set.user_id == user_id).order_by(Set.id)
        result = await session.execute(query)
        sets = result.mappings().all()
        return {
            "status": "success",
            "data": sets,
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.patch("/workout/update/{workout_id}")
async def update_workout(workout_id: int, update_data: WorkoutUpdate, user: User = Depends(current_user),
                         session: AsyncSession = Depends(get_async_session)):
    try:
        query = update(Workout).filter(Workout.id == workout_id).values(**update_data.model_dump(exclude_none=True))

        await session.execute(query)
        await session.commit()

        return {
            "status": "success",
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.patch("/exercise/update/{exercise_id}")
async def update_exercise(exercise_id: int, update_data: ExerciseUpdate, user: User = Depends(current_user),
                          session: AsyncSession = Depends(get_async_session)):
    if update_data.video:
        if update_data.video[:7] != "<iframe" or update_data.video[-7:] != "iframe>":
            update_data.video = ""

    try:
        query = update(Exercise).filter(Exercise.id == exercise_id).values(**update_data.model_dump(exclude_none=True))

        await session.execute(query)
        await session.commit()

        return {
            "status": "success",
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.patch("/set/update/{set_id}")
async def update_set(set_id: int, update_data: SetUpdate, user: User = Depends(current_user),
                     session: AsyncSession = Depends(get_async_session)):
    try:
        query = update(Set).filter(Set.id == set_id).values(**update_data.model_dump(exclude_none=True))

        await session.execute(query)
        await session.commit()

        return {
            "status": "success",
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.delete("/delete/created-workout")
async def delete_created_workout(workout_id: int, user: User = Depends(current_user),
                                 session: AsyncSession = Depends(get_async_session)):
    workout = await session.get(Workout, workout_id)

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    try:
        query_exercises = await session.execute(select(Exercise).filter(Exercise.workout_id == workout_id))
        exercises = query_exercises.mappings().all()
        for exercise in exercises:
            photos_exercise = await session.execute(
                select(Exercise_photo).filter(Exercise_photo.exercise_id == exercise.Exercise.id))
            result_photos_exercise = photos_exercise.mappings().all()
            for photo in result_photos_exercise:
                photo_path = os.path.join(f'src/{photo.Exercise_photo.photo}')
                if os.path.exists(photo_path):
                    os.remove(photo_path)

        del_workout = delete(Workout).filter(Workout.id == workout_id)

        await session.execute(del_workout)
        await session.commit()

        return {
            "status": "success",
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.delete("/delete/exercise")
async def delete_created_workout(exercise_id: int,
                                 user: User = Depends(current_user),
                                 session: AsyncSession = Depends(get_async_session)):
    exercise = await session.get(Exercise, exercise_id)

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    try:
        query_exercise = await session.execute(select(Exercise).filter(Exercise.id == exercise_id))
        exercise = query_exercise.mappings().one()

        photos_exercise = await session.execute(
            select(Exercise_photo).filter(Exercise_photo.exercise_id == exercise.Exercise.id))
        result_photos_exercise = photos_exercise.mappings().all()

        for photo in result_photos_exercise:
            photo_path = os.path.join(f'src/{photo.Exercise_photo.photo}')
            if os.path.exists(photo_path):
                os.remove(photo_path)

        del_exercise = delete(Exercise).filter(Exercise.id == exercise_id)

        await session.execute(del_exercise)
        await session.commit()

        return {
            "status": "success",
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.delete("/delete/added-workout")
async def delete_added_workout(workout_id: int, user_id: int, user: User = Depends(current_user),
                               session: AsyncSession = Depends(get_async_session)):
    workout = await session.get(Workout, workout_id)

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    try:
        query = delete(added_workouts_association).where(
            (added_workouts_association.c.workout_table == workout_id) and
            (added_workouts_association.c.user_table == user_id)
        )
        await session.execute(query)
        await session.commit()

        return {
            "status": "success",
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.delete("/delete/sets")
async def delete_added_sets(exercise_id: int, user_id: int, user: User = Depends(current_user),
                            session: AsyncSession = Depends(get_async_session)):
    try:
        query = delete(Set).where((Set.exercise_id == exercise_id) and (Set.user_id == user_id))
        await session.execute(query)
        await session.commit()

        return {
            "status": "success",
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.delete("/delete/photo")
async def delete_added_sets(exercise_id: int, photo_ids: list[int] = Query(),
                            user: User = Depends(current_user),
                            session: AsyncSession = Depends(get_async_session)):
    exercise = await session.get(Exercise, exercise_id)

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    try:
        query_photos = select(Exercise_photo).filter(Exercise_photo.id.in_(photo_ids))
        result_photos = await session.execute(query_photos)
        photos = result_photos.mappings().all()
        for photo in photos:
            photo_path = f"src/{photo['Exercise_photo'].photo}"
            if os.path.exists(photo_path):
                os.remove(photo_path)
        print("File deleted successfully")
        del_photos = delete(Exercise_photo).filter(Exercise_photo.id.in_(photo_ids))
        await session.execute(del_photos)
        await session.commit()

        return {
            "status": "success",
            "details": None,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail={
            "status": "error",
            "details": "File not found"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": str(e),
            "details": None,
        })
