from enum import Enum


class BaseUserGroups(str, Enum):
    pass


class UserPublicGroups(BaseUserGroups):
    player = 'player'


GROUP_PLAYER = 1
GROUP_ADMIN = 5


class UserAllGroups(BaseUserGroups):
    player = UserPublicGroups.player.value
    admin = 'admin'


all_group_map = {
    UserAllGroups.player: GROUP_PLAYER,
    UserAllGroups.player.value: GROUP_PLAYER,
    UserAllGroups.admin: GROUP_ADMIN,
    UserAllGroups.admin.value: GROUP_ADMIN
}
