from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status

from piaps.application.commands.payroll_item.create import (
    CreatePayrollItem,
    CreatePayrollItemRequest,
    CreatePayrollItemResponse,
)
from piaps.application.commands.payroll_item.delete import (
    DeletePayrollItem,
    DeletePayrollItemRequest,
)
from piaps.application.commands.payroll_item.update import (
    UpdatePayrollItem,
    UpdatePayrollItemData,
    UpdatePayrollItemRequest,
    UpdatePayrollItemResponse,
)
from piaps.application.queries.payroll_item.get_by_id import (
    GetPayrollItemById,
    GetPayrollItemByIdRequest,
    GetPayrollItemByIdResponse,
)
from piaps.application.queries.payroll_item.search import (
    SearchPayrollItems,
    SearchPayrollItemsRequest,
    SearchPayrollItemsResponse,
)
from piaps.domain.entities.payroll_item import PayrollItemId
from piaps.presentation.api.dependencies import get_current_user_token


router = APIRouter(prefix="/payroll-items", tags=["Payroll Items"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_payroll_item(
    request: CreatePayrollItemRequest,
    interactor: FromDishka[CreatePayrollItem],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> CreatePayrollItemResponse:
    return await interactor.execute(request)


@router.patch("/{payroll_item_id}", status_code=status.HTTP_200_OK)
async def update_payroll_item(
    payroll_item_id: PayrollItemId,
    data: UpdatePayrollItemData,
    interactor: FromDishka[UpdatePayrollItem],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> UpdatePayrollItemResponse:
    return await interactor.execute(UpdatePayrollItemRequest(id=payroll_item_id, data=data))


@router.delete("/{payroll_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payroll_item(
    payroll_item_id: PayrollItemId,
    interactor: FromDishka[DeletePayrollItem],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> None:
    await interactor.execute(DeletePayrollItemRequest(id=payroll_item_id))


@router.get("/{payroll_item_id}", status_code=status.HTTP_200_OK)
async def get_payroll_item_by_id(
    payroll_item_id: PayrollItemId,
    interactor: FromDishka[GetPayrollItemById],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> GetPayrollItemByIdResponse:
    return await interactor.execute(GetPayrollItemByIdRequest(id=payroll_item_id))


@router.get("", status_code=status.HTTP_200_OK)
async def search_payroll_items(
    interactor: FromDishka[SearchPayrollItems],
    request: Annotated[SearchPayrollItemsRequest, Depends()],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> SearchPayrollItemsResponse:
    return await interactor.execute(request)
