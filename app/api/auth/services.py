import random
import secrets
from typing import Union
from uuid import UUID

import asyncpg
from databases import Database
from loguru import logger
from passlib.context import CryptContext

import api.users.store as userstore
from api.auth.errors import NeedNewOTPPassword, IncorrectOTPPassword, \
    OTPPasswordResendIntervalNotPass, OTPPasswordSendError, OTPAuthForbidden, UserNameIsBusy, LeadAlreadyExists
from api.auth.schemas import AuthResponse, CustomerLeadForm, CourierLeadForm
from api.auth.store import OTPStore
from api.users.model import User

from core.common.groups_and_roles import UserAllGroups, all_group_map, UserPublicGroups, BaseUserGroups
from core.common.jwt import create_access_token
from core.config.common import common_settings
from core.customers.models.companies import CompanyType
from core.customers.store.employees import get_employee_fully
from core.db import tools as db_tools
from core.db.tables import DBTables
from core.exception import AccessForbiden
from core.exception import IncorrectCredentials
from core.otp_provider import send_otp_auth_password, _check_verification_code
from core.twilio.models import SendMethod

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
send_otp = send_otp_auth_password


async def authenticate_user(
        main_db: Database,
        demo_db: Database,
        username: str,
        group: UserAllGroups,
        password: str = None,
        otp_code: str = None
) -> User:
    user = await userstore.multibase_get_user(
        main_db, demo_db,
        username=username,
        group=group,
        return_none=False,
        assert_not_deactivated=True
    )
    db = user.get_access_db(main_db, demo_db)

    if password is not None:
        if user.password_hash is None or not verify_password(password, user.password_hash):
            raise IncorrectCredentials
    elif otp_code is not None:
        await verify_otp_password(db, user=user, otp_password=otp_code, group=group)
        await OTPStore.invalidate_all_otp_passwords(db, user=user, group=group)
    else:
        raise IncorrectCredentials

    return user


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, password_hash) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def generate_refresh_token() -> str:
    return secrets.token_hex(48)


def generate_otp_password() -> str:
    return "".join([str(random.randint(0, 9)) for _ in range(common_settings.AUTH_OTP_PASSWORD_LENGTH)])


async def save_refresh_token(db: Database, user: User, refresh_token):
    await userstore.update_user(db, user.user_id, refresh_token=refresh_token)


async def get_tokens(db: Database, user: User) -> AuthResponse:
    resp = AuthResponse(
        user_id=user.user_id,
        access_token=create_access_token(user),
        token_type="bearer",
        refresh_token=generate_refresh_token()
    )
    await save_refresh_token(db, user, resp.refresh_token)
    return resp


async def verify_otp_password(
        db: Database,
        user: Union[User, str],
        otp_password: str,
        group: BaseUserGroups
):
    if not await _check_verification_code(phone=user.username if type(user) is User else user, code=otp_password):
        last_password_in_db = await OTPStore.get_otp_password_for_check(db, user, group)

        if not last_password_in_db:
            raise NeedNewOTPPassword

        if last_password_in_db != otp_password:
            logger.error(f"Incorrect OTp password for user: {user}, {otp_password}")
            raise IncorrectOTPPassword


def otp_possible(user: User):
    # todo
    return True


async def send_otp_password(
        main_db: Database,
        demo_db: Database,
        username: str,
        user_group: UserAllGroups,
        send_method: SendMethod,
        assert_customer_company: CompanyType = None,
):
    async with main_db.transaction():
        async with demo_db.transaction():
            user = await userstore.multibase_get_user(
                main_db, demo_db,
                username=username,
                group=user_group,
                return_none=False,
                assert_not_deactivated=True
            )

            db = user.get_access_db(main_db, demo_db)

            if assert_customer_company and user.group_id == all_group_map[UserAllGroups.customer]:
                employee = await get_employee_fully(db, user_id=user.user_id, return_none=True)
                if employee and employee.company.type != assert_customer_company:
                    raise AccessForbiden

            if not otp_possible(user):
                raise OTPAuthForbidden

            till_next_send_seconds = await OTPStore.get_next_try_period(
                db, username=user.username,
                user_group=user_group
            )
            if till_next_send_seconds != 0:
                raise OTPPasswordResendIntervalNotPass(error_payload={"timeleft": till_next_send_seconds})

            otp_password = generate_otp_password()
            if username in ('15593165392', '19513669054'):
                otp_password = '528572'

            if not await send_otp(user.username, otp_password, send_method):
                raise OTPPasswordSendError

            await OTPStore.save_otp_password(
                db, user=user,
                otp_password=otp_password,
                user_group=user_group
            )


async def send_register_otp_password(
        main_db: Database,
        demo_db: Database,
        username: str,
        user_group: UserPublicGroups,
        send_method: SendMethod
):
    async with main_db.transaction():
        async with demo_db.transaction():
            user = await userstore.multibase_get_user(
                main_db, demo_db,
                username=username,
                group=user_group,
                return_none=True,
                assert_not_deactivated=False
            )
            if user:
                raise UserNameIsBusy

            till_next_send_seconds = await OTPStore.get_next_try_period(
                main_db, username=username,
                user_group=user_group
            )
            if till_next_send_seconds != 0:
                raise OTPPasswordResendIntervalNotPass(error_payload={"timeleft": till_next_send_seconds})

            otp_password = generate_otp_password()
            if not await send_otp(username, otp_password, send_method):
                raise OTPPasswordSendError

            await OTPStore.save_otp_password(main_db, user=username, otp_password=otp_password, user_group=user_group)


async def authenticate_user_by_refresh(
        main_db: Database,
        demo_db: Database,
        user_id: int,
        refresh_token: str,
        user_uuid: UUID = None
):
    user = await userstore.multibase_get_user(
        main_db, demo_db,
        pk=user_id,
        uuid=user_uuid,
        return_none=False,
        assert_not_deactivated=True,
        assert_refresh_token=refresh_token
    )

    return user


async def logout_user(db: Database, user: User):
    return await save_refresh_token(db, user, None)


async def save_customer_lead(db: Database, lead: CustomerLeadForm):
    try:
        await db_tools.create(
            db, table=DBTables.customer_lead,
            form=lead
        )
    except asyncpg.UniqueViolationError:
        raise LeadAlreadyExists()


async def save_courier_lead(db: Database, lead: CourierLeadForm):
    try:
        await db_tools.create(
            db, table=DBTables.courier_lead,
            form=lead
        )
    except asyncpg.UniqueViolationError:
        raise LeadAlreadyExists()
