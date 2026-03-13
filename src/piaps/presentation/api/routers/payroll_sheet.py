from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Body, Depends, status

from piaps.application.commands.payroll_sheet.add_record import (
    AddPayrollRecord,
    AddPayrollRecordData,
    AddPayrollRecordRequest,
    AddPayrollRecordResponse,
)
from piaps.application.commands.payroll_sheet.cancel import (
    CancelPayrollSheet,
    CancelPayrollSheetRequest,
    CancelPayrollSheetResponse,
)
from piaps.application.commands.payroll_sheet.confirm import (
    ConfirmPayrollSheet,
    ConfirmPayrollSheetRequest,
    ConfirmPayrollSheetResponse,
)
from piaps.application.commands.payroll_sheet.create import (
    CreatePayrollSheet,
    CreatePayrollSheetRequest,
    CreatePayrollSheetResponse,
)
from piaps.application.commands.payroll_sheet.remove_record import (
    RemovePayrollRecord,
    RemovePayrollRecordRequest,
    RemovePayrollRecordResponse,
)
from piaps.application.queries.payroll_sheet.get_by_id import (
    GetPayrollSheetById,
    GetPayrollSheetByIdRequest,
    GetPayrollSheetByIdResponse,
)
from piaps.application.queries.payroll_sheet.search import (
    SearchPayrollSheets,
    SearchPayrollSheetsRequest,
    SearchPayrollSheetsResponse,
)
from piaps.domain.entities.payroll_record import PayrollRecordId
from piaps.domain.entities.payroll_sheet import PayrollSheetId
from piaps.presentation.api.dependencies import get_current_user_token


router = APIRouter(prefix="/payroll-sheets", tags=["Payroll Sheets"], route_class=DishkaRoute)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_payroll_sheet(
    request: CreatePayrollSheetRequest,
    interactor: FromDishka[CreatePayrollSheet],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> CreatePayrollSheetResponse:
    return await interactor.execute(request)


@router.post("/{payroll_sheet_id}/records", status_code=status.HTTP_200_OK)
async def add_payroll_record(
    payroll_sheet_id: PayrollSheetId,
    data: Annotated[AddPayrollRecordData, Body()],
    interactor: FromDishka[AddPayrollRecord],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> AddPayrollRecordResponse:
    return await interactor.execute(
        AddPayrollRecordRequest(payroll_sheet_id=payroll_sheet_id, data=data)
    )


@router.delete("/{payroll_sheet_id}/records/{record_id}", status_code=status.HTTP_200_OK)
async def remove_payroll_record(
    payroll_sheet_id: PayrollSheetId,
    record_id: PayrollRecordId,
    interactor: FromDishka[RemovePayrollRecord],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> RemovePayrollRecordResponse:
    return await interactor.execute(
        RemovePayrollRecordRequest(payroll_sheet_id=payroll_sheet_id, record_id=record_id)
    )


@router.post("/{payroll_sheet_id}/confirm", status_code=status.HTTP_200_OK)
async def confirm_payroll_sheet(
    payroll_sheet_id: PayrollSheetId,
    interactor: FromDishka[ConfirmPayrollSheet],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> ConfirmPayrollSheetResponse:
    return await interactor.execute(ConfirmPayrollSheetRequest(id=payroll_sheet_id))


@router.post("/{payroll_sheet_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_payroll_sheet(
    payroll_sheet_id: PayrollSheetId,
    interactor: FromDishka[CancelPayrollSheet],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> CancelPayrollSheetResponse:
    return await interactor.execute(CancelPayrollSheetRequest(id=payroll_sheet_id))


@router.get("/{payroll_sheet_id}", status_code=status.HTTP_200_OK)
async def get_payroll_sheet_by_id(
    payroll_sheet_id: PayrollSheetId,
    interactor: FromDishka[GetPayrollSheetById],
    _token: Annotated[str, Depends(get_current_user_token)],
) -> GetPayrollSheetByIdResponse:
    return await interactor.execute(GetPayrollSheetByIdRequest(id=payroll_sheet_id))


@router.post("/search", status_code=status.HTTP_200_OK)
async def search_payroll_sheets(
    interactor: FromDishka[SearchPayrollSheets],
    request: SearchPayrollSheetsRequest,
    _token: Annotated[str, Depends(get_current_user_token)],
) -> SearchPayrollSheetsResponse:
    return await interactor.execute(request)
