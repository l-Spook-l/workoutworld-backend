from fastapi import APIRouter, Depends
from .base_config import auth_backend, fastapi_users
from .models import User
from .schemas import UserRead, UserCreate, UserUpdate, PasswordResetRequest, SendMessageAdmin
from fastapi.exceptions import HTTPException
from .manager import UserManager
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_async_session
from .utils import get_user_db, send_token_by_email, send_message_to_admin
import time

last_sent_time = 0
router = APIRouter()

# Authorization
router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"],
)
# Registration
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"],
)
# Password reset
router.include_router(
    fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"],
)
# User data update
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"],
)


@router.post("/request-password-reset")
async def request_password_reset(request: PasswordResetRequest, session: AsyncSession = Depends(get_async_session)):
    query_user = await session.execute(select(User).filter(User.email == request.email))
    user = query_user.one()[0]

    if not user:
        raise HTTPException(status_code=404, detail="Workout not found")

    user_manager = UserManager(get_user_db)
    reset_token = await user_manager.forgot_password(user)
    await send_token_by_email(user.email, reset_token)

    return {"message": "If the email exists, a password reset link has been sent.", 'token': reset_token}


@router.post('/send-message-admin')
async def send_message_admin(message: SendMessageAdmin):
    global last_sent_time

    current_time = time.time()
    time_difference = current_time - last_sent_time

    if time_difference >= 180:
        await send_message_to_admin(message.name, message.email, message.message)
        last_sent_time = current_time
        return {'status': 'success'}
    else:
        raise HTTPException(status_code=429, detail='You have already sent a message. '
                                                    'Please wait for 3 minutes before sending another message')
