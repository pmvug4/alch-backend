from enum import Enum

ROLE_ADMIN = 'admin'
ROLE_MANAGER = 'manager'


class BaseUserGroups(str, Enum):
    pass


class UserPublicGroups(BaseUserGroups):
    customer = 'customer'
    courier = 'courier'


GROUP_CUSTOMER = 1
GROUP_COURIER = 5

cooperator = 'cooperator'
GROUP_COOPERATOR = 100


class UserAllGroups(BaseUserGroups):
    customer = UserPublicGroups.customer.value
    courier = UserPublicGroups.courier.value
    cooperator = cooperator


all_group_map = {
    UserPublicGroups.customer: GROUP_CUSTOMER,
    UserPublicGroups.customer.value: GROUP_CUSTOMER,

    UserPublicGroups.courier: GROUP_COURIER,
    UserPublicGroups.courier.value: GROUP_COURIER,

    UserAllGroups.cooperator: GROUP_COOPERATOR,
    UserAllGroups.cooperator.value: GROUP_COOPERATOR
}
