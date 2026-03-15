# PiAPS API Documentation

## Перечисления
**Доменные enum для типов начислений, статусов, ролей пользователей.**

| Enum | Значения |
|------|----------|
| `PayrollItemType` | `accrual`, `deduction` |
| `PayrollCalculationType` | `fixed`, `percent` |
| `PayrollStatus` | `draft`, `confirmed`, `cancelled` |
| `UserRole` | `employee`(1), `accountant`(2), `administrator`(3) |

**Enum для типов операторов фильтрации**
| Enum | Значения |
|------|----------|
| `OperatorScalar` | `eq`, `ne`, `gt`, `ge`, `lt`, `le` |
| `OperatorStr` | `like`, `ilike` |
| `OperatorList` | `in`, `not_in` |
| `OperatorNull` | `is_null`, `is_not_null` |
| `SortDirection` | `asc`, `desc` |

## Value Objects
**Валидируемые примитивы с бизнес-логикой форматирования и ограничений.**

| VO | Поля | Ограничения |
|----|------|-------------|
| `Code` | `prefix: str`, `uid: str(8)` | формат `PREFIX-XXXXXXXX`, prefix: A-Z |
| `Name` | `value: str` | ≤100 chars, [a-zA-Zа-яё0-9\s.,!?;:()\\-'"` |
| `FullName` | `last_name`, `first_name`, `middle_name?` | только буквы+дефис, title case |
| `Username` | `value: str` | 3-30 chars, `[a-z0-9]` |
| `Password` | `value: str` | 8-64 chars, letters/digits/!@#$%^&*()_+... |
| `Money` | `value: Decimal` | 2 decimal places, ≤13 integer digits |

## DTO: Справочники
**View-модели для сериализации доменных сущностей.**

| Entity | View DTO поля |
|--------|---------------|
| **Department** | `id: UUID`, `code: str`, `name: str`, `description?: str` |
| **Position** | `id: UUID`, `code: str`, `name: str`, `base_salary: Decimal`, `description?: str` |
| **PayrollItem** | `id: UUID`, `code: str`, `name: str`, `payroll_type: PayrollItemType`, `calc_type: PayrollCalculationType`, `value?: Decimal` |
| **Employee** | `id: UUID`, `code: str`, `last_name: str`, `first_name: str`, `middle_name?: str`, `hire_date: date`, `department_id: UUID`, `position_id: UUID` |

## DTO: Payroll
**Иерархические DTO для ведомостей с рекурсивной вложенностью.**

| DTO | Поля |
|-----|------|
| **PayrollRecordView** | `id: UUID`, `employee_id: UUID`, `payroll_item: PayrollItemView`, `period: date`, `amount: Decimal`, `comment?: str` |
| **PayrollSheetView** | `id: UUID`, `employee_id: UUID`, `period: date`, `status: PayrollStatus`, `records: PayrollRecordView[]` |

## DTO: Query
**Универсальная система фильтрации, сортировки и пагинации для всех списков.**

| DTO | Поля |
|-----|------|
| **Filter** | `params: AnyFilter[]` (Scalar/Str/List/Null) |
| **Sort** | `params: SortParam[]` (`field`, `direction: SortDirection`) |
| **Pagination** | `page: int(1+)`, `page_size: int(1-100)` |
| **PaginationResult** | `data: T[]`, `meta: {total: int, total_pages: int, has_next: bool, has_prev: bool}` |
| **DateBetween** | `value_from?: date`, `value_to?: date` (from ≤ to) |

## Filter/Sort Fields
**Допустимые поля для фильтрации и сортировки по сущностям.**
| Entity       | Filter Fields                                                                      | Sort Fields                         |
| ------------ | ---------------------------------------------------------------------------------- | ----------------------------------- |
| Department   | code(str), name(str)                                                               | code, name                          |
| Position     | code(str), name(str), base_salary(decimal)                                         | code, name, base_salary             |
| PayrollItem  | code(str), name(str), payroll_type(enum), calc_type(enum)                          | code, name, payroll_type, calc_type |
| Employee     | code(str), full_name(str), hire_date(date), department_id(UUID), position_id(UUID) | code, full_name, hire_date          |
| PayrollSheet | employee_id(UUID), period(date), status(enum)                                      | period, status                      |
| User         | username(str), role(enum)                                                          | username, role                      |

## API Endpoints

### Аутентификация
**JWT авторизация с access/refresh токенами. Роли в payload токена.**

| Метод | Endpoint | Request | Response | Права |
|-------|----------|---------|----------|-------|
| `POST` | `/auth/register` | `{username: str, password: str}` | `{user: UserView}` | public |
| `POST` | `/auth/login` | `{username: str, password: str}` | `{access_token, refresh_token, token_type: "Bearer", user}` | public |
| `POST` | `/auth/refresh` | `{refresh_token: str}` | `{access_token, refresh_token, token_type, user}` | refresh token |

### Справочники (ADMIN)
**CRUD справочников с авто-генерацией уникальных кодов и проверкой уникальности имен.**

| Метод | Endpoint | Request | Response | Права |
|-------|----------|---------|----------|-------|
| `POST` | `/departments` | `{name: str, description?: str}` | `{department: DepartmentView}` | ADMIN |
| `PUT` | `/departments/:id` | `{data: {name?: str, description?: str}}` | `{department: DepartmentView}` | ADMIN |
| `DELETE` | `/departments/:id` | - | - | ADMIN |
| `POST` | `/positions` | `{name: str, base_salary: Decimal, description?: str}` | `{position: PositionView}` | ADMIN |
| `PUT` | `/positions/:id` | `{data: {name?: str\|NotSet, base_salary?: Decimal\|NotSet, description?: str\|NotSet}}` | `{position: PositionView}` | ADMIN |
| `DELETE` | `/positions/:id` | - | - | ADMIN |
| `POST` | `/payroll-items` | `{name: str, payroll_type, calc_type, value?: Decimal}` | `{payroll_item: PayrollItemView}` | ACCOUNTANT+ |
| `PUT` | `/payroll-items/:id` | `{data: {name?, payroll_type?, calc_type?, value?}}` | `{payroll_item: PayrollItemView}` | ACCOUNTANT+ |
| `DELETE` | `/payroll-items/:id` | - | - | ACCOUNTANT+ |

### Payroll (ACCOUNTANT+)
**Создание ведомостей, добавление/удаление записей, подтверждение/отмена. Авто-расчет сумм.**

| Метод | Endpoint | Request | Response | Права |
|-------|----------|---------|----------|-------|
| `POST` | `/payroll-sheets` | `{employee_id: UUID, period: date}` | `{payroll_sheet: PayrollSheetView}` | ACCOUNTANT+ |
| `POST` | `/payroll-sheets/:id/records` | `{data: {payroll_item_id: UUID, amount?: Decimal, comment?: str}}` | `{payroll_sheet: PayrollSheetView}` | ACCOUNTANT+ |
| `DELETE` | `/payroll-sheets/:id/records/:record_id` | - | `{payroll_sheet: PayrollSheetView}` | ACCOUNTANT+ |
| `POST` | `/payroll-sheets/:id/confirm` | - | `{payroll_sheet: PayrollSheetView}` | ACCOUNTANT+ |
| `POST` | `/payroll-sheets/:id/cancel` | - | `{payroll_sheet: PayrollSheetView}` | ACCOUNTANT+ |

**Бизнес-правила Payroll**:
- Лист уникален по `(employee_id, period)`
- `amount=null` → авто-расчет через `PayrollService.calculate()` на основе `base_salary`
- Изменения только в статусе `DRAFT`

### User Management (ADMIN+)
**Управление пользователями: создание, удаление, изменение пароля/роли/привязка сотрудника.**

| Метод | Endpoint | Request | Response | Права |
|-------|----------|---------|----------|-------|
| `POST` | `/users` | `{username, password, role, employee_id?: UUID}` | `{user: UserView}` | ADMIN |
| `DELETE` | `/users/:id` | - | - | ADMIN/self |
| `PATCH` | `/users/:id/username` | `{data: {username: str}}` | `{user: UserView}` | ADMIN/self |
| `PATCH` | `/users/:id/password` | `{data: {old_password?: str, new_password: str}}` | `{user: UserView}` | ADMIN/self |
| `PATCH` | `/users/:id/role` | `{data: {role: UserRole}}` | `{user: UserView}` | ADMIN |
| `PATCH` | `/users/:id/employee` | `{data: {employee_code?: str}}` | `{user: UserView}` | ADMIN/self |

### Read API (ACCOUNTANT+)
**Полнотекстовый поиск со сложными фильтрами, сортировкой и пагинацией.**

| Метод | Endpoint | Request | Response | Права |
|-------|----------|---------|----------|-------|
| `GET` | `/:entity/:id` | - | `EntityView` | ACCOUNTANT+ |
| `POST` | `/:entity/search` | `Filter?, Sort?, Pagination?` | `PaginationResult<EntityView[]>` | ACCOUNTANT+ |
| `GET` | `/me` | - | `{user: UserView}` | all |

**Entity**: `departments`, `positions`, `payroll-items`, `employees`, `payroll-sheets`, `users`

**PayrollSheet права**: EMPLOYEE видит только свои листы

### Reports (ACCOUNTANT+)
**Три типа отчетов с возможностью получения JSON данных или готового документа (PDF/Excel).**

| Метод | Endpoint | Request | Response | Права |
|-------|----------|---------|----------|-------|
| `POST` | `/reports/employee/:id` | `{period: DateBetween, status?, format?}` | `{data?: EmployeePayrollReportData, document?: ReportDocument}` | ACCOUNTANT+/self |
| `POST` | `/reports/department/:id` | `{period: DateBetween, status?, format?}` | `{data?: DepartmentPayrollReportData, document?}` | ACCOUNTANT+ |
| `POST` | `/reports/summary` | `{period: DateBetween, status?, format?}` | `{data?: PayrollSummaryReportData, document?}` | ACCOUNTANT+ |

## Ограничения уникальности
**Бизнес-правила уникальности на уровне домена:**
- `Department.name`, `Position.name`, `PayrollItem.name`
- `User.username`, `User.employee_id` (1:1)
- `PayrollSheet(employee_id, period)`

## Auto-генерация
**Уникальные коды генерируются автоматически при создании справочников:**
- `Code` для всех справочников (PREFIX-XXXXXXXX, уникальный, max 5 attempts)
