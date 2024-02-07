from typing import Optional
from uuid import uuid4

from fastapi import Depends, APIRouter, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import constr, EmailStr

from api.auth.errors import IncorrectOTPPassword, NeedNewOTPPassword, OTPAuthForbidden, \
    OTPPasswordResendIntervalNotPass, OTPPasswordSendError, UserNameIsBusy
from api.auth.schemas import AuthResponse, AuthOTP, RefreshToken, CustomerLeadForm, CourierLeadForm, DeliveryFrequency
from api.auth.services import authenticate_user, get_tokens, send_otp_password, \
    authenticate_user_by_refresh, logout_user, send_register_otp_password, save_customer_lead, save_courier_lead

import core.notices.store as notice_store
from core.common.groups_and_roles import UserAllGroups, UserPublicGroups
from core.common.security import get_current_user, apply_jwt_cookie, remove_jwt_cookie, GetCurrentDB
from core.config.common import common_settings
from core.config.smtp import smtp_settings
from core.customers.models.companies import CompanyType
from core.db import get_main_db, get_demo_db
from core.exception import IncorrectCredentials, AppZoneIsExpired
from core.models import phone_regex
from core.notices.depends import get_receiver
from core.notices.models import NoticeReceiver
from core.schemas import BaseOK, get_response_models, prepare_response_scheme
from core.smtp import send_mail
from core.twilio.models import SendMethod
from core.app_zone import AppZoneStore

router = APIRouter(tags=["auth"])

_possible_exceptions = [IncorrectCredentials]


@router.post(
    "",
    description="Авторизация. Получение токена JWT. Авторизация в соответствии с OAtuth2, по установленному паролю",
    response_model=AuthResponse,
    deprecated=True,
    responses=get_response_models("auth_post",
                                  _possible_exceptions,
                                  with_422_error=True,
                                  resp200ok=prepare_response_scheme(AuthResponse))
)
async def login_by_password(
        response: Response,
        user_group: UserAllGroups,
        form_data: OAuth2PasswordRequestForm = Depends(),
        main_db=Depends(get_main_db),
        demo_db=Depends(get_demo_db)
):
    user = await authenticate_user(
        main_db, demo_db,
        username=form_data.username,
        password=form_data.password,
        group=user_group
    )
    db = user.get_access_db(main_db, demo_db)

    auth_resp = await get_tokens(db, user)

    if common_settings.AUTH_BY_COOKIE:
        apply_jwt_cookie(response, auth_resp.access_token)

    return auth_resp


_possible_exceptions = [IncorrectCredentials, NeedNewOTPPassword, IncorrectOTPPassword]


@router.post(
    "/otp",
    description="Авторизация. Получение токена JWT. Авторизация через OTP пароль",
    response_model=AuthResponse,
    responses=get_response_models("post_auth_otp",
                                  _possible_exceptions,
                                  with_422_error=True,
                                  resp200ok=prepare_response_scheme(AuthResponse))
)
async def login_by_otp_password(
        response: Response,
        user_group: UserAllGroups,
        data: AuthOTP,
        main_db=Depends(get_main_db),
        demo_db=Depends(get_demo_db)
):
    user = await authenticate_user(
        main_db, demo_db,
        username=data.username,
        group=user_group,
        otp_code=data.password
    )
    db = user.get_access_db(main_db, demo_db)

    auth_resp = await get_tokens(db, user)

    if common_settings.AUTH_BY_COOKIE:
        apply_jwt_cookie(response, auth_resp.access_token)

    return auth_resp


_possible_exceptions = [IncorrectCredentials, OTPAuthForbidden, OTPPasswordResendIntervalNotPass, OTPPasswordSendError]


@router.get(
    "/otp/{username}",
    description="Запрос на получение OTP пароля",
    response_model=BaseOK,
    responses=get_response_models("get_auth_otp",
                                  _possible_exceptions,
                                  with_422_error=True,
                                  resp200ok=prepare_response_scheme(BaseOK))
)
async def otp_password_request(
        username: constr(regex=phone_regex),
        user_group: UserAllGroups,
        assert_customer_company: Optional[CompanyType] = None,
        send_method: SendMethod = SendMethod.sms,
        main_db=Depends(get_main_db),
        demo_db=Depends(get_demo_db)
):
    await send_otp_password(
        main_db, demo_db, username,
        user_group=user_group,
        assert_customer_company=assert_customer_company, send_method=send_method
    )
    return BaseOK()


_possible_exceptions = [UserNameIsBusy, OTPPasswordResendIntervalNotPass, OTPPasswordSendError]


@router.get(
    "/otp/{username}/register",
    description="Запрос на получение OTP пароля для регистрации пользователя",
    response_model=BaseOK,
    responses=get_response_models("get_auth_otp_register",
                                  _possible_exceptions,
                                  with_422_error=True,
                                  resp200ok=prepare_response_scheme(BaseOK))
)
async def get_otp_password_for_register(
        username: constr(regex=phone_regex),
        user_group: UserPublicGroups,
        send_method: SendMethod = SendMethod.sms,
        main_db=Depends(get_main_db),
        demo_db=Depends(get_demo_db)
):
    await send_register_otp_password(
        main_db, demo_db,
        username=username,
        user_group=user_group, send_method=send_method
    )
    return BaseOK()


_possible_exceptions = [IncorrectCredentials]


@router.post(
    "/refresh",
    description="Обновление токена",
    response_model=AuthResponse,
    responses=get_response_models("post_auth_refresh",
                                  _possible_exceptions,
                                  with_422_error=True,
                                  resp200ok=prepare_response_scheme(AuthResponse))
)
async def refresh_token(
        response: Response,
        data: RefreshToken,
        main_db=Depends(get_main_db),
        demo_db=Depends(get_demo_db)
):
    user = await authenticate_user_by_refresh(
        main_db, demo_db,
        user_id=data.user_id,
        user_uuid=data.user_uuid,
        refresh_token=data.refresh_token
    )
    db = user.get_access_db(main_db, demo_db)

    app_zone = await AppZoneStore.db_get(db, name=user.app_zone)
    if app_zone.expired:
        raise AppZoneIsExpired

    auth_resp = await get_tokens(db, user)

    if common_settings.AUTH_BY_COOKIE:
        apply_jwt_cookie(response, auth_resp.access_token)

    return auth_resp


@router.post(
    "/logout",
    description="Разлогин - удаление refresh токена",
    response_model=BaseOK,
    responses=get_response_models("post_auth_logout",
                                  [],
                                  with_422_error=False,
                                  resp200ok=prepare_response_scheme(BaseOK))
)
async def logout(
        response: Response,
        db=Depends(GetCurrentDB()),
        current_user=Depends(get_current_user),
        receiver: NoticeReceiver = Depends(get_receiver)
):
    await logout_user(db, current_user)
    await notice_store.NoticeReceiver.update_notice_receiver(
        db, receiver.id,
        app_token=None,
        platform=None
    )

    if common_settings.AUTH_BY_COOKIE:
        remove_jwt_cookie(response)

    return BaseOK()


@router.get(
    "/customer_leads",
    description="Отправка лида отправителя",
    response_model=BaseOK,
    responses=get_response_models("customer_lead",
                                  [],
                                  with_422_error=False,
                                  resp200ok=prepare_response_scheme(BaseOK))
)
async def customer_lead(
        email: EmailStr,
        phone: constr(regex=phone_regex),
        company_name: str,
        name: str,
        delivery_frequency: DeliveryFrequency,
        db=Depends(get_main_db),
        uuid: str = str(uuid4()),
):
    lead = CustomerLeadForm(uuid=uuid, email=email, phone=phone, name=name, company_name=company_name,
                            delivery_frequency=delivery_frequency)
    await save_customer_lead(db, lead)
    await send_mail(title="New customer lead!",
                    text=f"Email: {lead.email}\nPhone: {lead.phone}\nCompany Name: {lead.company_name}\nName: {lead.name}\nDelivery Frequency: {lead.delivery_frequency}",
                    receiver_email=smtp_settings.CUSTOMER_LEADS_RECEIVER)
    return BaseOK()


@router.get(
    "/courier_leads",
    description="Отправка лида курьера",
    response_model=BaseOK,
    responses=get_response_models("courier_lead",
                                  [],
                                  with_422_error=False,
                                  resp200ok=prepare_response_scheme(BaseOK))
)
async def courier_lead(
        email: EmailStr,
        phone: constr(regex=phone_regex),
        first_name: str,
        last_name: str = None,
        question: str = None,
        have_licence: bool = None,
        db=Depends(get_main_db),
        uuid: str = str(uuid4()),
):
    lead = CourierLeadForm(uuid=uuid, email=email, phone=phone, first_name=first_name,
                           last_name=last_name,
                           question=question, have_licence=have_licence)
    await save_courier_lead(db, lead)
    await send_mail(title="New courier lead!",
                    text=f"Email: {lead.email}\nPhone: {lead.phone}\nFull name: {lead.first_name.capitalize()} {lead.last_name.capitalize() if last_name else ''}\nQuestion: {lead.question if lead.question else '-'}\nHave Licence? - {lead.have_licence}",
                    receiver_email=smtp_settings.CUSTOMER_LEADS_RECEIVER)
    return BaseOK()
