from typing import Optional

from fastapi_users import schemas
from pydantic import Field
from pydantic import BaseModel


class UserRead(schemas.BaseUser[int]):
    id: int
    first_name: str
    last_name: str
    # email: str
    phone: str = None
    role_id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        # orm_mode = True
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    # email: str
    phone: str
    password: str = Field(min_length=8)
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: str


class PasswordReset(BaseModel):
    token: str
    new_password: str


class SendMessageAdmin(BaseModel):
    name: str
    email: str
    message: str
