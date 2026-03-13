from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status

from piaps.application.commands.user.bind_employee import (
    BindEmployee,
    BindEmployeeData,
    BindEmployeeRequest,
    BindEmployeeResponse,
)
from piaps.application.commands.user.change_password import (
    ChangePassword,
    ChangePasswordData,
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from piaps.application.commands.user.change_role import (
    ChangeUserRole,
    ChangeUserRoleData,
    ChangeUserRoleRequest,
    ChangeUserRoleResponse,
)
from piaps.application.commands.user.change_username import (
    ChangeUsername,
    ChangeUsernameData,
    ChangeUsernameRequest,
    ChangeUsernameResponse,
)
from piaps.application.commands.user.create import (
    CreateUser,
    CreateUserRequest,
    CreateUserResponse,
)
from piaps.application.commands.user.delete import DeleteUser, DeleteUserRequest
from piaps.application.queries.user.get_by_id import (
    GetUserById,
    GetUserByIdRequest,
    GetUserByIdResponse,
)
from piaps.application.queries.user.get_current import GetCurrentUser, GetCurrentUserResponse
from piaps.application.queries.user.search import (
    SearchUsers,
    SearchUsersRequest,
    SearchUsersResponse,
)
from piaps.domain.entities.user import UserId
from piaps.presentation.api.dependencies import get_current_user_token


router = APIRouter(prefix="/users", tags=["Users"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    interactor: FromDishka[CreateUser],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> CreateUserResponse:
    return await interactor.execute(request)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UserId,
    interactor: FromDishka[DeleteUser],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> None:
    await interactor.execute(DeleteUserRequest(id=user_id))


@router.patch("/{user_id}/username", status_code=status.HTTP_200_OK)
async def change_username(
    user_id: UserId,
    data: Annotated[ChangeUsernameData, Body()],
    interactor: FromDishka[ChangeUsername],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> ChangeUsernameResponse:
    return await interactor.execute(ChangeUsernameRequest(id=user_id, data=data))


@router.patch("/{user_id}/password", status_code=status.HTTP_200_OK)
async def change_password(
    user_id: UserId,
    data: Annotated[ChangePasswordData, Body()],
    interactor: FromDishka[ChangePassword],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> ChangePasswordResponse:
    return await interactor.execute(ChangePasswordRequest(id=user_id, data=data))


@router.patch("/{user_id}/role", status_code=status.HTTP_200_OK)
async def change_role(
    user_id: UserId,
    data: Annotated[ChangeUserRoleData, Body()],
    interactor: FromDishka[ChangeUserRole],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> ChangeUserRoleResponse:
    return await interactor.execute(ChangeUserRoleRequest(id=user_id, data=data))


@router.patch("/{user_id}/employee", status_code=status.HTTP_200_OK)
async def bind_employee(
    user_id: UserId,
    data: Annotated[BindEmployeeData, Body()],
    interactor: FromDishka[BindEmployee],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> BindEmployeeResponse:
    return await interactor.execute(BindEmployeeRequest(id=user_id, data=data))


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(
    interactor: FromDishka[GetCurrentUser],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> GetCurrentUserResponse:
    return await interactor.execute()


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: UserId,
    interactor: FromDishka[GetUserById],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> GetUserByIdResponse:
    return await interactor.execute(GetUserByIdRequest(id=user_id))


@router.post("/search", status_code=status.HTTP_200_OK)
async def search_users(
    interactor: FromDishka[SearchUsers],
    request: SearchUsersRequest,
    _token: Annotated[str, Depends(get_current_user_token)],
) -> SearchUsersResponse:
    return await interactor.execute(request)
