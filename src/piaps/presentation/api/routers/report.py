from typing import TYPE_CHECKING, Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from pydantic import TypeAdapter

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


if TYPE_CHECKING:
    from piaps.application.interfaces.reports.renderer import ReportDocument


router = APIRouter(prefix="/reports", tags=["Reports"], route_class=DishkaRoute)


def build_report_response(response_dto) -> Response:
    doc: ReportDocument | None = response_dto.document
    if doc is not None:
        return Response(
            content=doc.content,
            media_type=doc.mime_type,
            headers={"Content-Disposition": f'attachment; filename="{doc.filename}"'},
        )

    data = response_dto.data
    if data is None:
        return JSONResponse(content={})

    serialized = TypeAdapter(type(data)).dump_python(data, mode="json")
    return JSONResponse(content=serialized)


@router.post("/employee", status_code=status.HTTP_200_OK, response_class=Response)
async def get_employee_payroll_report(
    interactor: FromDishka[GetEmployeePayrollReport],
    request: GetEmployeePayrollReportRequest,
    _token: Annotated[str, Depends(get_current_user_token)],
) -> Response:
    result: GetEmployeePayrollReportResponse = await interactor.execute(request)
    return build_report_response(result)


@router.post("/department", status_code=status.HTTP_200_OK, response_class=Response)
async def get_department_payroll_report(
    interactor: FromDishka[GetDepartmentPayrollReport],
    request: GetDepartmentPayrollReportRequest,
    _token: Annotated[str, Depends(get_current_user_token)],
) -> Response:
    result: GetDepartmentPayrollReportResponse = await interactor.execute(request)
    return build_report_response(result)


@router.post("/summary", status_code=status.HTTP_200_OK, response_class=Response)
async def get_payroll_summary_report(
    interactor: FromDishka[GetPayrollSummaryReport],
    request: GetPayrollSummaryReportRequest,
    _token: Annotated[str, Depends(get_current_user_token)],
) -> Response:
    result: GetPayrollSummaryReportResponse = await interactor.execute(request)
    return build_report_response(result)
