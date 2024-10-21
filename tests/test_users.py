import pytest
from sqlalchemy import insert, select
from httpx import AsyncClient
from src.users.models import Role
from .conftest import async_session_maker, BaseTest


async def test_add_roles():
    async with async_session_maker() as session:
        stmt = insert(Role).values(id=1, name="admin")
        await session.execute(stmt)
        await session.commit()

        stmt = insert(Role).values(id=2, name="user")
        await session.execute(stmt)
        await session.commit()

        query = select(Role.id, Role.name)
        result = await session.execute(query)

        assert result.all() == [(1, 'admin'), (2, 'user')], "Roles not added"


class TestRegisterUser:
    @pytest.mark.parametrize("user_data, expected_status_code, expected_detail", [
        ({
             "email": "user1@example.com",
             "first_name": "User1_first name",
             "password": "valid_password",
             "last_name": "User1_last name",
             "phone": "0123456789"
         }, 201, {
             "id": 1,
             "email": "user1@example.com",
             "is_active": True,
             "is_superuser": False,
             "is_verified": False,
             "first_name": "User1_first name",
             "last_name": "User1_last name",
             "phone": "0123456789",
             "role_id": 2
         }),
        ({
             "email": "user2@example.com",
             "first_name": "User2_first name",
             "password": "valid_password",
             "last_name": "User2_last name",
             "phone": "9876543210"
         }, 201, {
             "id": 2,
             "email": "user2@example.com",
             "is_active": True,
             "is_superuser": False,
             "is_verified": False,
             "first_name": "User2_first name",
             "last_name": "User2_last name",
             "phone": "9876543210",
             "role_id": 2
         })
    ])
    async def test_register_user(self, ac: AsyncClient, test_data, user_data, expected_status_code, expected_detail):
        response = await ac.post("/api/users/register", json=user_data)

        assert response.status_code == expected_status_code
        assert response.json() == expected_detail
        user_id = response.json().get("id")
        assert user_id in [1, 2]

        if user_id == 1:
            test_data["first_user_id"] = user_id
        elif user_id == 2:
            test_data["second_user_id"] = user_id

    @pytest.mark.parametrize("user_data, expected_status_code, expected_detail", [
        ({
             "email": "",
             "password": "",
             "first_name": "",
             "last_name": "",
             "phone": ""
         }, 422, {'detail': [{'type': 'value_error', 'loc': ['body', 'email'],
                              'msg': 'value is not a valid email address: The email '
                                     'address is not valid. It must have exactly one @-sign.',
                              'input': '',
                              'ctx': {'reason': 'The email address is not valid. It must have exactly one @-sign.'}},
                             {'type': 'string_too_short', 'loc': ['body', 'password'],
                              'msg': 'String should have at least 8 characters', 'input': '', 'ctx': {'min_length': 8}},
                             {'type': 'string_too_short', 'loc': ['body', 'first_name'],
                              'msg': 'String should have at least 5 characters', 'input': '', 'ctx': {'min_length': 5}},
                             {'type': 'string_too_short', 'loc': ['body', 'last_name'],
                              'msg': 'String should have at least 5 characters', 'input': '',
                              'ctx': {'min_length': 5}}]}),
        ({
             "email": "test@example.com",
             "password": "short",
             "first_name": "",
             "last_name": "",
             "phone": ""
         }, 422, {'detail': [
            {'type': 'string_too_short', 'loc': ['body', 'password'], 'msg': 'String should have at least 8 characters',
             'input': 'short', 'ctx': {'min_length': 8}},
            {'type': 'string_too_short', 'loc': ['body', 'first_name'],
             'msg': 'String should have at least 5 characters',
             'input': '', 'ctx': {'min_length': 5}},
            {'type': 'string_too_short', 'loc': ['body', 'last_name'],
             'msg': 'String should have at least 5 characters',
             'input': '', 'ctx': {'min_length': 5}}]}),
        ({
             "email": "test@example.com",
             "password": "valid_password",
             "first_name": "J",
             "last_name": "",
             "phone": ""
         }, 422, {'detail': [
            {'type': 'string_too_short', 'loc': ['body', 'first_name'],
             'msg': 'String should have at least 5 characters',
             'input': 'J', 'ctx': {'min_length': 5}},
            {'type': 'string_too_short', 'loc': ['body', 'last_name'],
             'msg': 'String should have at least 5 characters',
             'input': '', 'ctx': {'min_length': 5}}]}),
        ({
             "email": "test@example.com",
             "password": "valid_password",
             "first_name": "Oliver",
             "last_name": "",
             "phone": ""
         }, 422, {'detail': [
            {'type': 'string_too_short', 'loc': ['body', 'last_name'],
             'msg': 'String should have at least 5 characters',
             'input': '', 'ctx': {'min_length': 5}}]}),
        ({
             "email": "user1@example.com",
             "password": "valid_password",
             "first_name": "Oliver",
             "last_name": "Johnson",
             "phone": ""
         }, 400, {
             "detail": "REGISTER_USER_ALREADY_EXISTS"
         })
    ])
    async def test_register_user_error(self, ac: AsyncClient, user_data, expected_status_code, expected_detail):
        response = await ac.post("/api/users/register", json=user_data)
        assert response.status_code == expected_status_code
        assert response.json() == expected_detail


class TestLoginUser:
    @pytest.mark.parametrize("user_data, expected_status_code, expected_detail", [
        ({
             "username": "user1@example.com",
             "password": "valid_password"
         }, 200, {'detail': "LOGIN_BAD_CREDENTIALS"}),
    ])
    async def test_login(self, ac: AsyncClient, user_data, expected_status_code, expected_detail):
        response = await ac.post("/api/users/jwt/login", data=user_data)

        assert response.status_code == expected_status_code
        token = response.json().get("access_token")
        assert token is not None

    @pytest.mark.parametrize("user_data, expected_status_code, expected_detail", [
        ({
             "username": "wrong_email.com",
             "password": "valid_password"
         }, 400, {'detail': "LOGIN_BAD_CREDENTIALS"}),
        ({
             "username": "user1@example.com",
             "password": "wrong"
         }, 400, {'detail': "LOGIN_BAD_CREDENTIALS"}),
    ])
    async def test_login_error(self, ac: AsyncClient, user_data, expected_status_code, expected_detail):
        response = await ac.post("/api/users/jwt/login", data=user_data)
        assert response.status_code == expected_status_code
        assert response.json() == expected_detail


class TestGetUser(BaseTest):
    async def test_get_user(self, ac: AsyncClient, test_data):
        headers = self.get_headers(user_id=test_data["user_id"])
        response = await ac.get("/api/users/me", headers=headers)

        assert response.status_code == 200
        assert response.json() == {'id': 1, 'email': 'user1@example.com', 'is_active': True, 'is_superuser': False,
                                   'is_verified': False, 'first_name': 'User1_first name',
                                   'last_name': 'User1_last name',
                                   'phone': '0123456789', 'role_id': 2}

    @pytest.mark.parametrize("token, expected_status_code, expected_detail", [
        (None, 401, {'detail': 'Unauthorized'}),
        ("invalid_token", 401, {'detail': 'Unauthorized'}),
    ])
    async def test_get_user_error(self, ac: AsyncClient, token, expected_status_code, expected_detail, test_data):
        headers = {}
        if token:
            headers = {"Authorization": f"Bearer {token}"}

        response = await ac.get("/api/users/me", headers=headers)

        assert response.status_code == expected_status_code
        assert response.json() == expected_detail

