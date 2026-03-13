from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status

from piaps.application.commands.position.create import (
    CreatePosition,
    CreatePositionRequest,
    CreatePositionResponse,
)
from piaps.application.commands.position.delete import DeletePosition, DeletePositionRequest
from piaps.application.commands.position.update import (
    UpdatePosition,
    UpdatePositionData,
    UpdatePositionRequest,
    UpdatePositionResponse,
)
from piaps.application.queries.position.get_by_id import (
    GetPositionById,
    GetPositionByIdRequest,
    GetPositionByIdResponse,
)
from piaps.application.queries.position.search import (
    SearchPositions,
    SearchPositionsRequest,
    SearchPositionsResponse,
)
from piaps.domain.entities.position import PositionId
from piaps.presentation.api.dependencies import get_current_user_token


router = APIRouter(prefix="/positions", tags=["Positions"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_position(
    request: CreatePositionRequest,
    interactor: FromDishka[CreatePosition],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> CreatePositionResponse:
    return await interactor.execute(request)


@router.patch("/{position_id}", status_code=status.HTTP_200_OK)
async def update_position(
    position_id: PositionId,
    data: UpdatePositionData,
    interactor: FromDishka[UpdatePosition],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> UpdatePositionResponse:
    return await interactor.execute(UpdatePositionRequest(id=position_id, data=data))


@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: PositionId,
    interactor: FromDishka[DeletePosition],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> None:
    await interactor.execute(DeletePositionRequest(id=position_id))


@router.get("/{position_id}", status_code=status.HTTP_200_OK)
async def get_position_by_id(
    position_id: PositionId,
    interactor: FromDishka[GetPositionById],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> GetPositionByIdResponse:
    return await interactor.execute(GetPositionByIdRequest(id=position_id))


@router.get("", status_code=status.HTTP_200_OK)
async def search_positions(
    interactor: FromDishka[SearchPositions],
    request: Annotated[SearchPositionsRequest, Depends()],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> SearchPositionsResponse:
    return await interactor.execute(request)
