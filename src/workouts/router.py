from pydantic import ValidationError
from fastapi import APIRouter, Depends, Query, UploadFile, Form
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound

from src.core.database import get_async_session
from src.core.dependencies import get_workout_service, get_exercise_service, get_set_service
from src.users.base_config import current_user
from src.users.models import User
from src.workouts.schemas import WorkoutCreate, ExerciseCreate, SetCreate, WorkoutUpdate, ExerciseUpdate, SetUpdate
from src.workouts.service import WorkoutService, ExerciseService, SetService

router = APIRouter(
    prefix="/workouts",
    tags=["workouts"]
)


@router.post("/create_workout", dependencies=[Depends(current_user)])
async def add_workout(
        new_workout: WorkoutCreate,
        service: WorkoutService = Depends(get_workout_service),
):
    workout_id = await service.create_workout(new_workout)
    return {"status": "success", "workout_ID": workout_id}


@router.post("/create_exercise", dependencies=[Depends(current_user)])
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
        service: ExerciseService = Depends(get_exercise_service),
):
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

        exercise_id = await service.create_exercise(exercise_data, photos)
        return {"status": "success", "exercise_ID": exercise_id}
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field = error['loc'][0]
            msg = error['msg']
            error_messages.append(f"Error in field '{field}': {msg}")
        raise HTTPException(status_code=422, detail=error_messages)


@router.post("/create_set", dependencies=[Depends(current_user)])
async def add_set(
        number_sets: int,
        new_set: SetCreate,
        service: SetService = Depends(get_set_service),
):
    try:
        await service.create_set(number_sets, new_set)
        return {"status": "success"}
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.post("/add-workout-to-user/{user_id}/{workout_id}")
async def add_workout_to_user(
        user_id: int,
        workout_id: int,
        user: User = Depends(current_user),
        service: WorkoutService = Depends(get_workout_service),
):
    # TODO try: - проблема с ошибками
    await service.add_user_workout_association(user, user_id, workout_id)

    return {"status": "success", "message": "Workout added to user"}
    # except Exception:
    #     raise HTTPException(status_code=500, detail={
    #         "status": "error",
    #         "data": None,
    #         "details": None,
    #     })


@router.post("/add-new-photos", dependencies=[Depends(current_user)])
async def add_new_photos_exercise(
        exercise_id: int,
        exercise_name: str,
        photos: list[UploadFile] = None,
        service: ExerciseService = Depends(get_exercise_service),
):
    try:
        await service.add_new_photos_exercise(exercise_id, exercise_name, photos)
        return {"status": "success", "exercise_ID": exercise_id}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e)


@router.get("/")  # TODO наверно изменить роут
async def get_workouts(
        name: str = Query(None, description="Filter by name"),
        difficulty: list[str] = Query(None, description="Filter by difficulty"),
        skip: int = Query(0, description="Number of records to skip"),
        limit: int = Query(12, description="Number of records to return"),
        page: int = Query(1, description="Page number"),
        service: WorkoutService = Depends(get_workout_service),
):
    try:
        workouts, total_count = await service.get_filtered_workouts(
            name=name,
            difficulty=difficulty,
            skip=skip,
            limit=limit,
        )

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
async def get_one_workout(
        workout_id: int,
        user_id: int = None,
        service: WorkoutService = Depends(get_workout_service),
):
    try:
        workout = await service.get_one_workout(workout_id, user_id)
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


@router.get("/active-workout", dependencies=[Depends(current_user)])
async def get_active_workout(
        workout_id: int,
        user_id: int,
        service: WorkoutService = Depends(get_workout_service),
):
    try:
        workout = await service.get_active_workout(workout_id, user_id)
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


@router.get("/user-workouts", dependencies=[Depends(current_user)])
async def get_user_workouts(
        user_id: int,
        name: str = Query(None, description="Filter by name"),
        difficulty: list[str] = Query(None, description="Filter by difficulty"),
        skip: int = Query(0, description="Number of records to skip"),
        limit: int = Query(9, description="Number of records to return"),
        is_public: bool = Query(None, description="Filter by status"),
        page: int = Query(1, description="Page number"),
        service: WorkoutService = Depends(get_workout_service),
):
    try:
        user_workouts, total_count = await service.get_filtered_workouts(
            user_id=user_id,
            name=name,
            difficulty=difficulty,
            skip=skip,
            limit=limit,
            is_public=is_public
        )

        return {
            "status": "success",
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


@router.get("/get-user-added-workouts/{user_id}", dependencies=[Depends(current_user)])
async def get_user_added_workouts(
        user_id: int,
        name: str = Query(None, description="Filter by name"),
        difficulty: list[str] = Query(None, description="Filter by difficulty"),
        skip: int = Query(0, description="Number of records to skip"),
        limit: int = Query(9, description="Number of records to return"),
        page: int = Query(1, description="Page number"),
        service: WorkoutService = Depends(get_workout_service),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        user_workouts, total_count = await service.get_user_added_workouts(
            session=session,
            user_id=user_id,
            name=name,
            difficulty=difficulty,
            skip=skip,
            limit=limit
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
async def get_difficulties(
        service: WorkoutService = Depends(get_workout_service),
):
    try:
        difficulties = await service.get_workout_difficulties()
        return {
            "status": "success",
            "data": difficulties,
            "details": None,
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None,
        })


@router.get("/sets", dependencies=[Depends(current_user)])
async def get_sets(
        user_id: int,
        exercise_ids: list[int] = Query(None),
        service: SetService = Depends(get_set_service),
):
    try:
        sets = await service.get_sets(user_id, exercise_ids)
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


# TODO проверить роут на корректность обновления другим пользователем
@router.patch("/workout/update/{workout_id}", dependencies=[Depends(current_user)])
async def update_workout(
        workout_id: int,
        update_data: WorkoutUpdate,
        service: WorkoutService = Depends(get_workout_service),
):
    try:
        await service.update_workout(workout_id, update_data)
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


@router.patch("/exercise/update/{exercise_id}", dependencies=[Depends(current_user)])
async def update_exercise(
        exercise_id: int,
        update_data: ExerciseUpdate,
        service: ExerciseService = Depends(get_exercise_service),
):
    try:
        await service.update_exercise(exercise_id, update_data)
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


@router.patch("/set/update/{set_id}", dependencies=[Depends(current_user)])
async def update_set(
        set_id: int,
        update_data: SetUpdate,
        service: SetService = Depends(get_set_service),
):
    try:
        await service.update_set(set_id=set_id, data=update_data)
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


@router.delete("/delete/created-workout", dependencies=[Depends(current_user)])
async def delete_created_workout(
        workout_id: int,
        service: WorkoutService = Depends(get_workout_service),
):
    await service.delete_created_workout(workout_id=workout_id)
    return {
        "status": "success",
        "details": None,
    }


@router.delete("/delete/exercise", dependencies=[Depends(current_user)])
async def delete_created_exercise(
        exercise_id: int,
        service: ExerciseService = Depends(get_exercise_service),
):
    await service.delete_created_exercise(exercise_id=exercise_id)
    return {
        "status": "success",
        "details": None,
    }


# может поменять роуты местами
@router.delete("/delete/added-workout", dependencies=[Depends(current_user)])
async def delete_added_workout(
        workout_id: int,
        user_id: int,
        service: WorkoutService = Depends(get_workout_service),
):
    try:
        await service.delete_added_workout(user_id=user_id, workout_id=workout_id)
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


@router.delete("/delete/sets", dependencies=[Depends(current_user)])
async def delete_added_sets(
        exercise_id: int,
        user_id: int,
        service: SetService = Depends(get_set_service),
):
    try:
        await service.delete_set(exercise_id=exercise_id, user_id=user_id)
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


@router.delete("/delete/photo", dependencies=[Depends(current_user)])
async def delete_photo(
        exercise_id: int,
        photo_ids: list[int] = Query(),
        service: ExerciseService = Depends(get_exercise_service),
):
    try:
        await service.delete_photo(exercise_id=exercise_id, photo_ids=photo_ids)
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
