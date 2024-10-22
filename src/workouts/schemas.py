from typing import Optional
from pydantic import BaseModel, Field


class WorkoutCreate(BaseModel):
    name: str
    user_id: int
    description: str
    is_public: bool
    difficulty: str
    total_time: str


class ExerciseCreate(BaseModel):
    name: str
    workout_id: int
    description: str
    number_of_sets: int = Field(ge=1)
    maximum_repetitions: int = Field(ge=1)
    rest_time: int = Field(ge=1)
    video: Optional[str | None]
    number_in_workout: int


class SetCreate(BaseModel):
    exercise_id: int
    user_id: int
    repetition: int = Field(ge=0)
    weight: int = Field(ge=0)


class WorkoutUpdate(BaseModel):
    name: str = None
    description: str = None
    is_public: bool = None
    difficulty: str = None
    total_time: str = None


class ExerciseUpdate(BaseModel):
    name: str = None
    description: str = None
    number_of_sets: Optional[int | None] = Field(ge=1)
    maximum_repetitions: Optional[int | None] = Field(ge=1)
    rest_time: Optional[int | None] = Field(ge=1)
    video: Optional[str | None]


class SetUpdate(BaseModel):
    repetition: Optional[int | None] = Field(ge=0)
    weight: Optional[int | None] = Field(ge=0)
