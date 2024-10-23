import jwt
from datetime import datetime, timedelta, timezone
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from src.core.config import ADMIN_SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            payload = {
                "username": username,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            }

            token = jwt.encode(payload, ADMIN_SECRET_KEY, algorithm="HS256")
            request.session.update({"token": token})
            return True

        return False

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


authentication_backend = AdminAuth(secret_key=ADMIN_SECRET_KEY)
