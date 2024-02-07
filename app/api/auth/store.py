import datetime
from typing import Optional, Union

from databases import Database
from core.common.groups_and_roles import all_group_map, BaseUserGroups
from api.users.model import User
from core.config.common import common_settings


from loguru import logger


class OTPStore:

    @classmethod
    async def save_otp_password(
            cls, db: Database,
            user: Union[User, str],
            otp_password,
            user_group: BaseUserGroups,
            valid_period_seconds: Optional[int] = None
    ) -> None:

        if isinstance(user, User):
            _username = user.username
            user_id = user.user_id
        else:
            _username = user
            user_id = None

        _valid_period = valid_period_seconds or common_settings.AUTH_OTP_PASSWORD_VALID_PERIOD_SECONDS
        valid_until = datetime.datetime.utcnow() + datetime.timedelta(seconds=_valid_period)
        check_count = common_settings.AUTH_OTP_PASSWORD_CHECKS

        sql = f"""
                      INSERT INTO otp_passwords (user_id, username,  otp_password, valid_until, check_count, group_id) 
                      VALUES (:user_id, :username, :otp_password, :valid_until, :check_count, :group_id);
    
            """
        try:
            await db.execute(sql, {
                "user_id": user_id,
                "username": _username,
                "group_id": all_group_map[user_group],
                "otp_password": otp_password,
                "valid_until": valid_until,
                "check_count": check_count
            })
        except Exception as e:
            logger.exception(f"{repr(e)}")
            pass

    @classmethod
    async def get_otp_password_for_check(
            cls, db: Database,
            user: Union[User, str],
            group_id: BaseUserGroups
    ) -> Optional[int]:
        bindings = dict()
        if type(user) is User:
            condition = "user_id=:user_id"
            bindings.update({"user_id": user.user_id})
        else:
            condition = "username=:username"
            bindings.update({"username": user})
        bindings.update({"group_id": all_group_map[group_id]})
        now = datetime.datetime.utcnow()
        sql = f"""
                             WITH updated  as
                                 (
                                     UPDATE otp_passwords SET check_count = check_count-1                              
                                     WHERE 
                                           {condition} 
                                           AND valid_until > :now
                                           AND check_count > 0
                                           AND invalid = 0 
                                           AND group_id = :group_id 
                                     RETURNING otp_password, group_id,  created_at
                                 )
                             select otp_password, group_id, created_at from updated
                             ORDER BY created_at DESC
                             LIMIT 1

               """

        bindings.update({"now": now})
        try:
            res = await db.execute(sql, bindings)
        except Exception as e:
            logger.exception(f"{repr(e)}")
            return None
        logger.info(f"{res=}")
        return res or None

    @classmethod
    async def get_next_try_period(
            cls, db: Database,
            username: str,
            user_group: BaseUserGroups
    ) -> int:
        """
        возвращает количество секунд через сколько повторно можно запросить OTP пароль
        """

        sql = f"""                                     
                                     select created_at  from otp_passwords
                                    
                                     WHERE username=:username AND group_id=:group_id
                                           
                                     ORDER BY created_at DESC
                                     LIMIT 1

                       """
        try:
            res = await db.execute(sql, {"username": username, "group_id": all_group_map[user_group]})
        except Exception as e:
            logger.exception(f"{repr(e)}")
            return common_settings.AUTH_OTP_RETRY_PERIOD_SECONDS

        if not res:
            return 0

        sec_from_last_try = datetime.datetime.utcnow() - res
        sec_from_last_try = sec_from_last_try.total_seconds()

        if common_settings.AUTH_OTP_RETRY_PERIOD_SECONDS > sec_from_last_try:
            return int(common_settings.AUTH_OTP_RETRY_PERIOD_SECONDS - sec_from_last_try)

        return 0

    @classmethod
    async def invalidate_all_otp_passwords(
            cls, db: Database,
            user: Union[User, str],
            group: BaseUserGroups
    ) -> bool:
        if isinstance(user, User):
            _username = user.username

        else:
            _username = user

        sql = f"""

                     UPDATE otp_passwords SET invalid = 1                             
                     WHERE username=:username AND group_id=:group_id 
                           AND invalid = 0 
                           
               """
        try:
            await db.execute(sql, {"username": _username, "group_id": all_group_map[group]})
        except Exception as e:
            logger.exception(f"{repr(e)}")
            return False
        return True
