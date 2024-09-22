import time
from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_async_session
from src.core.redis import get_redis_client
from .base_config import auth_backend, fastapi_users
from .models import User
from .schemas import UserRead, UserCreate, UserUpdate, PasswordResetRequest, SendMessageAdmin
from .manager import UserManager
from .utils import get_user_db, send_token_by_email
from .tasks import send_message_to_admin


router = APIRouter()

# Authorization
router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/users/jwt", tags=["users"],
)
# Registration
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), prefix="/users", tags=["users"],
)
# Password reset
router.include_router(
    fastapi_users.get_reset_password_router(), prefix="/users", tags=["users"],
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
async def send_message_admin(
        message: SendMessageAdmin,
        request: Request,
        redis_client: Redis = Depends(get_redis_client)
):
    # Получаем IP-адрес пользователя
    user_ip = request.client.host
    user_key = f"user_last_message:{user_ip}"  # Используем IP-адрес как ключ

    current_time = time.time()

    # Попытка получить время последнего сообщения
    last_sent_time = await redis_client.get(user_key)
    if last_sent_time is not None:
        time_difference = current_time - float(last_sent_time)
        if time_difference < 180:
            raise HTTPException(status_code=429, detail='You have already sent a message. '
                                                        'Please wait for 3 minutes before sending another message.')

    try:
        # Сохранение текущего времени отправки
        await redis_client.set(user_key, current_time, ex=180)  # Время жизни ключа – 3 минуты
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

    try:
        # Отправка задачи в Celery
        send_message_to_admin.delay(message.name, message.email, message.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Celery error: {str(e)}")

    return {'status': 'success'}
