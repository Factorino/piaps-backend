from decimal import Decimal

from piaps.domain.entities.payroll import Payroll
from piaps.domain.entities.salary_item import SalaryItem
from piaps.domain.enums.payroll_calculation_type import PayrollCalculationType
from piaps.domain.value_objects.money import Money
from piaps.domain.value_objects.payroll_line_item import PayrollLineItem


class PayrollService:
    def add_accrual(
        self,
        payroll: Payroll,
        accrual: SalaryItem,
        amount: Decimal | None = None,
        comment: str | None = None,
    ) -> Payroll:
        money_amount: Decimal = amount if amount is not None else accrual.value

        if accrual.calc_type == PayrollCalculationType.PERCENT:
            net_salary: Money = payroll.net_salary
            money_amount = net_salary.value * money_amount / 100

        money = Money(value=money_amount)
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
        amount: Decimal | None = None,
        comment: str | None = None,
    ) -> Payroll:
        money_amount: Decimal = amount if amount is not None else deduction.value

        if deduction.calc_type == PayrollCalculationType.PERCENT:
            net_salary: Money = payroll.net_salary
            money_amount = net_salary.value * money_amount / 100

        money = Money(value=money_amount)
        item = PayrollLineItem(
            salary_item_id=deduction.id,
            amount=money,
            comment=comment,
        )

        payroll.add_deduction(item)
        return payroll
