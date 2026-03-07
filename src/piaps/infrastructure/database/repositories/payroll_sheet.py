from sqlalchemy.ext.asyncio import AsyncSession

from piaps.application.interfaces.repositories.payroll_sheet import IPayrollSheetRepository
from piaps.domain.entities.payroll_record import PayrollRecord
from piaps.domain.entities.payroll_sheet import PayrollSheet, PayrollSheetId
from piaps.infrastructure.database.models.payroll_record import PayrollRecordORM
from piaps.infrastructure.database.models.payroll_sheet import PayrollSheetORM
from piaps.infrastructure.database.repositories.base import SAAbstractRepository

def _record_entity_to_orm(record: PayrollRecord, sheet_id: PayrollSheetId) -> PayrollRecordORM:
    return PayrollRecordORM(
        id=record.id,
        employee_id=record.employee_id,
        payroll_item_id=record.payroll_item.id,
        period=record.period,
        amount=record.amount.value,
        comment=record.comment,
        payroll_sheet_id=sheet_id,
    )


def _sheet_entity_to_orm(sheet: PayrollSheet) -> PayrollSheetORM:
    orm = PayrollSheetORM(
        id=sheet.id,
        employee_id=sheet.employee_id,
        period=sheet.period,
        status=sheet.status,
    )
    orm.records = [_record_entity_to_orm(r, sheet.id) for r in sheet.records]
    return orm



class SAPayrollSheetRepository(
    IPayrollSheetRepository, SAAbstractRepository[PayrollSheet, PayrollSheetORM]
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _to_orm(self, entity: PayrollSheet) -> PayrollSheetORM:
        return _sheet_entity_to_orm(entity)
