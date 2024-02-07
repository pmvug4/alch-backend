from databases import Database


from api.auth.services import verify_otp_password
from api.users.errors import UserCreationError
from api.users.store import create_user_in_db
from api.auth.store import OTPStore

from core.common.groups_and_roles import all_group_map, UserPublicGroups


async def register_user(
        db: Database,
        username: str,
        otp_password: str,
        group: UserPublicGroups,
        app_zone: str = None
):
    await verify_otp_password(db, user=username, otp_password=otp_password, group=group)
    await OTPStore.invalidate_all_otp_passwords(db, user=username, group=group)

    user_id = await create_user_in_db(
        db, username,
        all_group_map[group],
        app_zone=app_zone
    )
    if not user_id:
        raise UserCreationError
    return user_id
