import pytest
from sqlalchemy import insert, select
from httpx import AsyncClient
from src.workouts.models import DifficultyWorkout
from .conftest import async_session_maker, BaseTest


class TestDifficulties:
    async def test_add_difficulties(self):
        async with async_session_maker() as session:
            await session.execute(insert(DifficultyWorkout).values(difficulty="Easy"))
            await session.execute(insert(DifficultyWorkout).values(difficulty="Medium"))
            await session.execute(insert(DifficultyWorkout).values(difficulty="Hard"))

            await session.commit()

            query = select(DifficultyWorkout.id, DifficultyWorkout.difficulty)
            result = await session.execute(query)

            assert result.all() == [(1, "Easy"), (2, "Medium"), (3, "Hard")], "The complexity did not increase"

    async def test_get_difficulties(self, ac: AsyncClient):
        response = await ac.get("/api/workouts/workout-difficulties")

        assert response.status_code == 200
        assert response.json() == {'status': 'success',
                                   'data': [{'DifficultyWorkout': {'difficulty': 'Easy', 'id': 1}},
                                            {'DifficultyWorkout': {'difficulty': 'Medium', 'id': 2}},
                                            {'DifficultyWorkout': {'difficulty': 'Hard', 'id': 3}}],
                                   'details': None}


class TestCreateWorkout(BaseTest):
    async def test_create_workout(self, ac: AsyncClient, test_data):
        headers = self.get_headers(user_id=test_data["first_user_id"])
        response = await ac.post("/api/workouts/create_workout", json={
            "name": "Workout one",
            "user_id": test_data["first_user_id"],
            "description": "description workout_one",
            "is_public": False,
            "difficulty": "Hard",
            "total_time": ""
        }, headers=headers)

        assert response.status_code == 200
        assert response.json() == {"status": "success", "workout_ID": 1}

        test_data["workout_id"] = response.json().get("workout_ID")

    async def test_create_exercise_first(self, ac: AsyncClient, test_data):
        headers = self.get_headers(user_id=test_data["first_user_id"])
        data = {
            "name": "exercise 1",
            "workout_id": test_data["workout_id"],
            "description": "description exercise",
            "number_of_sets": 1,
            "maximum_repetitions": 12,
            "rest_time": 60,
            "video": "",
            "number_in_workout": 1
        }
        response = await ac.post("/api/workouts/create_exercise", data=data, headers=headers)

        assert response.status_code == 200
        assert response.json().get("status") == "success"

        test_data["first_exercise_id"] = response.json().get("exercise_ID")

    async def test_create_exercise_second(self, ac: AsyncClient, test_data):
        headers = self.get_headers(user_id=test_data["first_user_id"])
        data = {
            "name": "exercise 2",
            "workout_id": test_data["workout_id"],
            "description": "description exercise 2",
            "number_of_sets": 1,
            "maximum_repetitions": 8,
            "rest_time": 180,
            "video": "",  # or we provide the correct iframe video
            "number_in_workout": 2
        }
        response = await ac.post("/api/workouts/create_exercise", data=data, headers=headers)

        assert response.status_code == 200
        assert response.json().get("status") == "success"

        test_data["second_exercise_id"] = response.json().get("exercise_ID")

    async def test_create_set_first_exercise(self, ac: AsyncClient, test_data):
        headers = self.get_headers(user_id=test_data["first_user_id"])
        response = await ac.post("/api/workouts/create_set", params={
            "number_sets": 3
        }, json={
            "exercise_id": test_data["first_exercise_id"],
            "user_id": test_data["first_user_id"],
            "repetition": 5,
            "weight": 10
        }, headers=headers)

        assert response.status_code == 200
        assert response.json() == {"status": "success"}

    async def test_create_set_second_exercise(self, ac: AsyncClient, test_data):
        headers = self.get_headers(user_id=test_data["first_user_id"])
        response = await ac.post("/api/workouts/create_set", params={
            "number_sets": 5
        }, json={
            "exercise_id": test_data["second_exercise_id"],
            "user_id": test_data["first_user_id"],
            "repetition": 5,
            "weight": 10
        }, headers=headers)

        assert response.status_code == 200
        assert response.json() == {"status": "success"}


class TestGetWorkout(BaseTest):
    async def test_get_workouts(self, ac: AsyncClient):
        response = await ac.get("/api/workouts/")

        assert response.status_code == 200
        assert response.json().get("status") == "success"

    async def test_get_selected_workout(self, ac: AsyncClient, test_data):
        response = await ac.get("/api/workouts/workout/1", params={
            "user_id": test_data["first_user_id"],
        })

        assert response.status_code == 200
        assert response.json().get("status") == "success"

    async def test_get_user_workouts(self, ac: AsyncClient, test_data):
        headers = self.get_headers(user_id=test_data["first_user_id"])
        response = await ac.get("/api/workouts/workout/1", params={
            "user_id": test_data["first_user_id"],
        }, headers=headers)

        assert response.status_code == 200
        assert response.json().get("status") == "success"

    async def test_get_user_workouts_error(self, ac: AsyncClient, test_data):
        response = await ac.get("/api/workouts/user-workouts", params={
            "user_id": test_data["first_user_id"],
        })

        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized"}

    async def test_get_active_workouts(self, ac: AsyncClient, test_data):
        response = await ac.get("/api/workouts/user-workouts", params={
            "user_id": test_data["first_user_id"],
        })

        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized"}


class TestAddWorkout(BaseTest):
    @pytest.mark.parametrize("user_id, expected_status_code, expected_detail", [
        (1, 400, {"detail": "This workout cannot be added to the workout creator"}),
        (2, 200, {"status": "success", "message": "Workout added to user"}),
    ])
    async def test_add_workout_to_user(self, ac: AsyncClient, user_id, expected_status_code, expected_detail):
        headers = self.get_headers(user_id=user_id)
        response = await ac.post("/api/workouts/add-workout-to-user/1/1", headers=headers)

        assert response.status_code == expected_status_code
        assert response.json() == expected_detail

    @pytest.mark.parametrize("user_id, expected_status_code, expected_detail", [
        (1, 200, {"status": "success", "message": "Workout added to user"}),
        (2, 200, {"status": "success", "message": "Workout added to user"}),
    ])
    async def test_get_user_added_workouts(self, ac: AsyncClient, user_id, expected_status_code, expected_detail):
        headers = self.get_headers(user_id=user_id)
        response = await ac.get("/api/workouts/get-user-added-workouts/2", headers=headers)

        assert response.status_code == expected_status_code
        assert response.json().get("status") == "success"


class TestDeleteWorkout(BaseTest):
    async def test_delete_added_workout(self, ac: AsyncClient, test_data):
        headers = self.get_headers(user_id=test_data["first_user_id"])
        response = await ac.delete("/api/workouts/delete/added-workout", params={
            "workout_id": 1,
            "user_id": 1
        }, headers=headers)

        assert response.status_code == 200
        assert response.json() == {"status": "success", "details": None}

    async def test_delete_exercise(self, ac: AsyncClient, test_data):
        headers = self.get_headers(user_id=test_data["first_user_id"])
        response = await ac.delete("/api/workouts/delete/exercise", params={
            "exercise_id": 2
        }, headers=headers)

        assert response.status_code == 200
        assert response.json() == {"status": "success", "details": None}

    async def test_delete_created_workout(self, ac: AsyncClient, test_data):
        headers = self.get_headers(user_id=test_data["first_user_id"])
        response = await ac.delete("/api/workouts/delete/created-workout", params={
            "workout_id": 1
        }, headers=headers)

        assert response.status_code == 200
        assert response.json() == {"status": "success", "details": None}
