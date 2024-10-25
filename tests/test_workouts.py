import pytest
from sqlalchemy import insert, select
from httpx import AsyncClient
from src.workouts.models import DifficultyWorkout
from .conftest import async_session_maker, BaseTest


class TestDifficulties:
    async def test_add_difficulties(self):
        async with async_session_maker() as session:
            stmt = insert(DifficultyWorkout).values(difficulty="Easy")
            await session.execute(stmt)
            await session.commit()

            stmt = insert(DifficultyWorkout).values(difficulty="Medium")
            await session.execute(stmt)
            await session.commit()

            stmt = insert(DifficultyWorkout).values(difficulty="Hard")
            await session.execute(stmt)
            await session.commit()

            query = select(DifficultyWorkout.id, DifficultyWorkout.difficulty)
            result = await session.execute(query)

            assert result.all() == [(1, "Easy"), (2, "Medium"), (3, "Hard")], "The complexity did not increase"

    async def test_get_difficulties(self, ac: AsyncClient):
        response = await ac.get("/api/workouts/workout-difficulties")

        assert response.status_code == 200
        assert response.json() == {'status': 'success', 'data': [{'DifficultyWorkout': {'difficulty': 'Easy', 'id': 1}},
                                                                 {'DifficultyWorkout': {'difficulty': 'Medium',
                                                                                        'id': 2}},
                                                                 {'DifficultyWorkout': {'difficulty': 'Hard',
                                                                                        'id': 3}}], 'details': None}


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
