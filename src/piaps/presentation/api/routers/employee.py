from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status

from piaps.application.commands.employee.create import (
    CreateEmployee,
    CreateEmployeeRequest,
    CreateEmployeeResponse,
)
from piaps.application.commands.employee.delete import DeleteEmployee, DeleteEmployeeRequest
from piaps.application.commands.employee.update import (
    UpdateEmployee,
    UpdateEmployeeData,
    UpdateEmployeeRequest,
    UpdateEmployeeResponse,
)
from piaps.application.queries.employee.get_by_id import (
    GetEmployeeById,
    GetEmployeeByIdRequest,
    GetEmployeeByIdResponse,
)
from piaps.application.queries.employee.search import (
    SearchEmployees,
    SearchEmployeesRequest,
    SearchEmployeesResponse,
)
from piaps.domain.entities.employee import EmployeeId
from piaps.presentation.api.dependencies import get_current_user_token


router = APIRouter(prefix="/employees", tags=["Employees"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_employee(
    request: CreateEmployeeRequest,
    interactor: FromDishka[CreateEmployee],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> CreateEmployeeResponse:
    return await interactor.execute(request)


@router.patch("/{employee_id}", status_code=status.HTTP_200_OK)
async def update_employee(
    employee_id: EmployeeId,
    data: Annotated[UpdateEmployeeData, Body()],
    interactor: FromDishka[UpdateEmployee],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> UpdateEmployeeResponse:
    return await interactor.execute(UpdateEmployeeRequest(id=employee_id, data=data))


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: EmployeeId,
    interactor: FromDishka[DeleteEmployee],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> None:
    await interactor.execute(DeleteEmployeeRequest(id=employee_id))


@router.get("/{employee_id}", status_code=status.HTTP_200_OK)
async def get_employee_by_id(
    employee_id: EmployeeId,
    interactor: FromDishka[GetEmployeeById],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> GetEmployeeByIdResponse:
    return await interactor.execute(GetEmployeeByIdRequest(id=employee_id))


@router.post("/search", status_code=status.HTTP_200_OK)
async def search_employees(
    interactor: FromDishka[SearchEmployees],
    request: SearchEmployeesRequest,
    _token: Annotated[str, Depends(get_current_user_token)],
) -> SearchEmployeesResponse:
    return await interactor.execute(request)
