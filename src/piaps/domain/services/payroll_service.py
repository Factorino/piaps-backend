from decimal import Decimal

from piaps.domain.entities.payroll import Payroll
from piaps.domain.entities.salary_item import SalaryItem
from piaps.domain.enums.calculation_type import CalculationType
from piaps.domain.value_objects.money import Money
from piaps.domain.value_objects.payroll_line_item import PayrollLineItem


class PayrollService:
    def add_accrual(
        self,
        payroll: Payroll,
        accrual: SalaryItem,
        comment: str | None = None,
    ) -> Payroll:
        if accrual.calc_type == CalculationType.FIXED:
            money = Money(value=Decimal(accrual.value))
        elif accrual.calc_type == CalculationType.PERCENT:
            net_salary: Money = payroll.net_salary
            amount: Decimal = net_salary.value * accrual.value / 100
            money = Money(value=amount)
        else:
            raise ValueError(f"Unsupported calculation type: {accrual.calc_type}")

        item = PayrollLineItem(
            salary_item_id=accrual.id,
            amount=money,
            comment=comment,
        )

        payroll.add_accrual(item)
        return payroll

    def add_deduction(
        self,
        payroll: Payroll,
        deduction: SalaryItem,
        comment: str | None = None,
    ) -> Payroll:
        if deduction.calc_type == CalculationType.FIXED:
            money = Money(value=Decimal(deduction.value))
        elif deduction.calc_type == CalculationType.PERCENT:
            net_salary: Money = payroll.net_salary
            amount: Decimal = net_salary.value * deduction.value / 100
            money = Money(value=amount)
        else:
            raise ValueError(f"Unsupported calculation type: {deduction.calc_type}")

        item = PayrollLineItem(
            salary_item_id=deduction.id,
            amount=money,
            comment=comment,
        )

        payroll.add_deduction(item)
        return payroll
