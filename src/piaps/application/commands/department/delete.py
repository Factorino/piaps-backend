from typing import TYPE_CHECKING
from uuid import UUID

from piaps.application.common.dto import dto
from piaps.application.errors.base import NotFoundError
from piaps.application.interfaces.interactor import IInteractor
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.repositories.department import IDepartmentRepository
from piaps.application.interfaces.transaction_manager import TransactionManager


if TYPE_CHECKING:
    from piaps.domain.entities.department import Department


@dto
class DeleteDepartmentRequest:
    id: UUID


@dto
class DeleteDepartmentResponse:
    success: bool


class DeleteDepartment(IInteractor[DeleteDepartmentRequest, DeleteDepartmentResponse]):
    def __init__(
        self,
        department_repository: IDepartmentRepository,
        department_reader: IDepartmentReader,
        uow: TransactionManager,
    ) -> None:
        self._repository: IDepartmentRepository = department_repository
        self._reader: IDepartmentReader = department_reader
        self._uow: TransactionManager = uow

    async def execute(self, request: DeleteDepartmentRequest) -> DeleteDepartmentResponse:
        department: Department | None = await self._reader.find_by_id(request.id)
        if department is None:
            raise NotFoundError

        await self._repository.delete(department)
        await self._uow.commit()

        return DeleteDepartmentResponse(success=True)
