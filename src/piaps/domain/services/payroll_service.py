from piaps.domain.entities.payroll_item import PayrollItem
from piaps.domain.enums.payroll_calculation_type import PayrollCalculationType
from piaps.domain.errors.payroll import InvalidCalculationTypeError, PayrollValueNotSetError
from piaps.domain.value_objects.money import Money


class PayrollService:
    def calculate(
        self,
        payroll_item: PayrollItem,
        base_salary: Money,
        amount: Money | None = None,
    ) -> Money:
        match payroll_item.calc_type:
            case PayrollCalculationType.FIXED:
                return self._fixed(payroll_item, amount)
            case PayrollCalculationType.PERCENT:
                return self._percent(payroll_item, base_salary)
            case _:
                raise InvalidCalculationTypeError(
                    f"Unsupported calculation type: '{payroll_item.calc_type}'"
                )

    def _fixed(self, payroll_item: PayrollItem, amount: Money | None) -> Money:
        if amount is not None:
            return amount
        if payroll_item.value is None:
            raise PayrollValueNotSetError(
                f"PayrollItem '{payroll_item.code.value}' has no fixed value set"
            )
        return Money(value=payroll_item.value)

    def _percent(self, payroll_item: PayrollItem, base_salary: Money) -> Money:
        if payroll_item.value is None:
            raise PayrollValueNotSetError(
                f"PayrollItem '{payroll_item.code.value}' has no percent rate set"
            )
        return base_salary * payroll_item.value
