from uuid import UUID

from piaps.application.common.dto import base
from piaps.application.errors.base import NotFoundError
from piaps.application.interfaces.interactor import IInteractor
from piaps.application.interfaces.readers.department import IDepartmentReader
from piaps.application.interfaces.repositories.department import IDepartmentRepository
from piaps.application.interfaces.transaction_manager import TransactionManager
from piaps.domain.entities.department import Department


@base
class UpdateDepartmentRequest:
    id: UUID
    name: str | None = None
    description: str | None = None


@base
class UpdateDepartmentResponse:
    department: Department


class UpdateDepartment(IInteractor[UpdateDepartmentRequest, UpdateDepartmentResponse]):
    def __init__(
        self,
        department_repository: IDepartmentRepository,
        department_reader: IDepartmentReader,
        uow: TransactionManager,
    ) -> None:
        self._repository: IDepartmentRepository = department_repository
        self._reader: IDepartmentReader = department_reader
        self._uow: TransactionManager = uow

    async def execute(self, request: UpdateDepartmentRequest) -> UpdateDepartmentResponse:
        existing: Department | None = await self._reader.find_by_id(request.id)
        if existing is None:
            raise NotFoundError

        updated = Department(
            id=existing.id,
            code=existing.code,
            name=request.name if request.name is not None else existing.name,
            description=request.description
            if request.description is not None
            else existing.description,
        )

        saved: Department = await self._repository.update(updated)
        await self._uow.commit()

        return UpdateDepartmentResponse(department=saved)
