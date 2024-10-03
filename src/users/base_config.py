from fastapi_users.authentication import BearerTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy
from fastapi_users import FastAPIUsers
from src.core.config import SECRET_KEY
from .manager import get_user_manager
from .models import User

# Cookie configuration
bearer_transport = BearerTransport(tokenUrl="users/jwt/login")


# JWT
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=2592000)


# JWT authentication
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Getting the user
current_user = fastapi_users.current_user()
