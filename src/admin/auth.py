import jwt
from datetime import datetime, timedelta, timezone
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request


ADMIN_secret_key = "Hewq@kw4lfmS34L"


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        # После проверки имени пользователя и пароля
        payload = {
            "username": username,  # Можно добавить другие данные, например, роли
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),  # Время жизни токена
        }

        # Создание токена
        token = jwt.encode(payload, ADMIN_secret_key, algorithm="HS256")
        # Validate username/password credentials
        # And update session
        request.session.update({"token": token})

        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        # Check the token in depth
        return True


authentication_backend = AdminAuth(secret_key=ADMIN_secret_key)
