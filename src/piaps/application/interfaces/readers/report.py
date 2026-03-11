from abc import abstractmethod
from typing import Protocol

from piaps.application.common.dto.query.between import DateBetween
from piaps.application.common.dto.report.department_payroll import DepartmentPayrollReportData
from piaps.application.common.dto.report.employee_payroll import EmployeePayrollReportData
from piaps.application.common.dto.report.payroll_summary import PayrollSummaryReportData
from piaps.domain.entities.department import DepartmentId
from piaps.domain.entities.employee import EmployeeId
from piaps.domain.enums.payroll_status import PayrollStatus


class IPayrollReportReader(Protocol):
    @abstractmethod
    async def get_employee_payroll_report(
        self,
        employee_id: EmployeeId,
        period: DateBetween,
    ) -> EmployeePayrollReportData: ...

    @abstractmethod
    async def get_department_payroll_report(
        self,
        department_id: DepartmentId,
        period: DateBetween,
        status: PayrollStatus | None = None,
    ) -> DepartmentPayrollReportData: ...

    @abstractmethod
    async def get_payroll_summary_report(
        self,
        period: DateBetween,
        status: PayrollStatus | None = None,
    ) -> PayrollSummaryReportData: ...
