from __future__ import annotations  # Makes importing models unnecessary
from datetime import datetime
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from fastapi_users.db import SQLAlchemyBaseUserTable
from src.core.database import Base


class Role(Base):
    __tablename__ = "role_table"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    name: Mapped[str] = mapped_column(String(length=99), nullable=False)

    user: Mapped[list["User"]] = relationship(back_populates="role")

    def __str__(self):
        return self.name


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    username: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(length=99), nullable=False)
    last_name: Mapped[str] = mapped_column(String(99), nullable=False)
    phone: Mapped[str | None] = mapped_column(nullable=False)
    registered_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    role_id: Mapped[int] = mapped_column(ForeignKey("role_table.id"))

    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    role: Mapped["Role"] = relationship(back_populates="user")
    created_workouts: Mapped[list["Workout"]] = relationship(back_populates="user", cascade="all")
    added_workouts: Mapped[list["Workout"] | None] = relationship(secondary="added_workouts_association", cascade="all")
    set: Mapped[list["Set"]] = relationship(back_populates="user", cascade="all")

    def __str__(self):
        return self.first_name
