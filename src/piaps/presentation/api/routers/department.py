from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status

from piaps.application.commands.department.create import (
    CreateDepartment,
    CreateDepartmentRequest,
    CreateDepartmentResponse,
)
from piaps.application.commands.department.delete import DeleteDepartment, DeleteDepartmentRequest
from piaps.application.commands.department.update import (
    UpdateDepartment,
    UpdateDepartmentData,
    UpdateDepartmentRequest,
    UpdateDepartmentResponse,
)
from piaps.application.queries.department.get_by_id import (
    GetDepartmentById,
    GetDepartmentByIdRequest,
    GetDepartmentByIdResponse,
)
from piaps.application.queries.department.search import (
    SearchDepartments,
    SearchDepartmentsRequest,
    SearchDepartmentsResponse,
)
from piaps.domain.entities.department import DepartmentId
from piaps.presentation.api.dependencies import get_current_user_token


router = APIRouter(prefix="/departments", tags=["Departments"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_department(
    request: CreateDepartmentRequest,
    interactor: FromDishka[CreateDepartment],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> CreateDepartmentResponse:
    return await interactor.execute(request)


@router.patch("/{department_id}", status_code=status.HTTP_200_OK)
async def update_department(
    department_id: DepartmentId,
    data: Annotated[UpdateDepartmentData, Body()],
    interactor: FromDishka[UpdateDepartment],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> UpdateDepartmentResponse:
    return await interactor.execute(UpdateDepartmentRequest(id=department_id, data=data))


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: DepartmentId,
    interactor: FromDishka[DeleteDepartment],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> None:
    await interactor.execute(DeleteDepartmentRequest(id=department_id))


@router.get("/{department_id}", status_code=status.HTTP_200_OK)
async def get_department_by_id(
    department_id: DepartmentId,
    interactor: FromDishka[GetDepartmentById],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> GetDepartmentByIdResponse:
    return await interactor.execute(GetDepartmentByIdRequest(id=department_id))


@router.get("", status_code=status.HTTP_200_OK)
async def search_departments(
    interactor: FromDishka[SearchDepartments],
    request: Annotated[SearchDepartmentsRequest, Depends()],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> SearchDepartmentsResponse:
    return await interactor.execute(request)
