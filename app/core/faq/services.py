from databases import Database
from core.common.groups_and_roles import GROUP_CUSTOMER, GROUP_COURIER
from core.customers.models import EmployeeRole
from core.customers.store import get_employee_fully
from api.users.model import User
from .exceptions import FaqAccessDenied
from .models import Role


async def assert_role_faq(
        db: Database,
        user: User,
        role: Role
) -> bool:
    if user.group_id == GROUP_COURIER and role.value != Role.courier:
        raise FaqAccessDenied
    if user.group_id == GROUP_CUSTOMER:
        employee = await get_employee_fully(db, user_id=user.user_id)
        if employee.role == EmployeeRole.admin and role != Role.client:
            raise FaqAccessDenied
        elif employee.role == EmployeeRole.manager and role != Role.manager:
            raise FaqAccessDenied
    return True
