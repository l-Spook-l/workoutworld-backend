from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.core.database import Base


added_workouts_association = Table(
    "added_workouts_association",
    Base.metadata,
    Column("workout_table", ForeignKey("workout_table.id")),
    Column("user_table", ForeignKey("user_table.id")),
)


class Workout(Base):
    __tablename__ = "workout_table"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    name: Mapped[str] = mapped_column(String(length=256))
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    description: Mapped[str] = mapped_column(String(length=1000))
    is_public: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    difficulty: Mapped[str]
    total_time: Mapped[str] = mapped_column(String(length=999))

    user: Mapped["User"] = relationship(back_populates="created_workouts")
    exercise: Mapped[list["Exercise"]] = relationship(back_populates="workout", cascade="all, delete-orphan",
                                                      order_by="Exercise.number_in_workout")

    def __str__(self):
        return self.name


class Exercise(Base):
    __tablename__ = "exercise_table"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    name: Mapped[str] = mapped_column(String(length=256))
    workout_id: Mapped[int] = mapped_column(ForeignKey("workout_table.id", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(String(length=500))
    number_of_sets: Mapped[int]
    maximum_repetitions: Mapped[int]
    rest_time: Mapped[int | None]
    video: Mapped[str | None]
    number_in_workout: Mapped[int | None]

    workout: Mapped["Workout"] = relationship(back_populates="exercise")
    set: Mapped[list["Set"]] = relationship(back_populates="exercise", cascade="all, delete-orphan")
    photo: Mapped[list["Exercise_photo"]] = relationship(back_populates="exercise", cascade="all, delete-orphan")

    def __str__(self):
        return self.name


class Set(Base):
    __tablename__ = "set_table"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise_table.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    repetition: Mapped[int]
    weight: Mapped[int]

    exercise: Mapped["Exercise"] = relationship(back_populates="set")
    user: Mapped["User"] = relationship(back_populates="set")

    def __str__(self):
        return f"Set with {self.repetition} repetitions and {self.weight} kg" if self.repetition and self.weight else "Incomplete Set"


class Exercise_photo(Base):
    __tablename__ = "exercise_photo_table"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercise_table.id", ondelete="CASCADE"))
    photo: Mapped[str | None]

    exercise: Mapped["Exercise"] = relationship(back_populates="photo")

    def __str__(self):
        return self.photo or "No photo"


class DifficultyWorkout(Base):
    __tablename__ = "difficulty_workout_table"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    difficulty: Mapped[str]

    def __str__(self):
        return self.difficulty
