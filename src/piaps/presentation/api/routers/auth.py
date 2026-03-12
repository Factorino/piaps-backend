from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from piaps.application.commands.auth.login_user import (
    LoginUser,
    LoginUserRequest,
    LoginUserResponse,
)
from piaps.application.commands.auth.refresh_token import (
    RefreshToken,
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from piaps.application.commands.auth.register_user import (
    RegisterUser,
    RegisterUserRequest,
    RegisterUserResponse,
)


router = APIRouter(prefix="/auth", tags=["Auth"], route_class=DishkaRoute)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterUserRequest,
    interactor: FromDishka[RegisterUser],
) -> RegisterUserResponse:
    return await interactor.execute(request)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    interactor: FromDishka[LoginUser],
) -> LoginUserResponse:
    return await interactor.execute(
        LoginUserRequest(username=form.username, password=form.password)
    )


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    request: RefreshTokenRequest,
    interactor: FromDishka[RefreshToken],
) -> RefreshTokenResponse:
    return await interactor.execute(request)
