from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, status

from piaps.application.queries.report.department_payroll import (
    GetDepartmentPayrollReport,
    GetDepartmentPayrollReportRequest,
    GetDepartmentPayrollReportResponse,
)
from piaps.application.queries.report.employee_payroll import (
    GetEmployeePayrollReport,
    GetEmployeePayrollReportRequest,
    GetEmployeePayrollReportResponse,
)
from piaps.application.queries.report.payroll_summary import (
    GetPayrollSummaryReport,
    GetPayrollSummaryReportRequest,
    GetPayrollSummaryReportResponse,
)
from piaps.presentation.api.dependencies import get_current_user_token


router = APIRouter(prefix="/reports", tags=["Reports"], route_class=DishkaRoute)


@router.post("/employee-payroll", status_code=status.HTTP_200_OK)
async def get_employee_payroll_report(
    interactor: FromDishka[GetEmployeePayrollReport],
    request: GetEmployeePayrollReportRequest,
    _token: Annotated[str, Depends(get_current_user_token)],
) -> GetEmployeePayrollReportResponse:
    return await interactor.execute(request)


@router.post("/department-payroll", status_code=status.HTTP_200_OK)
async def get_department_payroll_report(
    interactor: FromDishka[GetDepartmentPayrollReport],
    request: GetDepartmentPayrollReportRequest,
    _token: Annotated[str, Depends(get_current_user_token)],
) -> GetDepartmentPayrollReportResponse:
    return await interactor.execute(request)


@router.post("/payroll-summary", status_code=status.HTTP_200_OK)
async def get_payroll_summary_report(
    interactor: FromDishka[GetPayrollSummaryReport],
    request: GetPayrollSummaryReportRequest,
    _token: Annotated[str, Depends(get_current_user_token)],
) -> GetPayrollSummaryReportResponse:
    return await interactor.execute(request)
