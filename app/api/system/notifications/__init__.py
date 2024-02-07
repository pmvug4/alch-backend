from fastapi import APIRouter, Depends
from pydantic import BaseModel, constr, root_validator
from typing import Optional

from core.schemas import get_response_models, prepare_response_scheme, BaseOK
from core.common.security import OnlyFor, GetCurrentDB, AccessServer
from core import notification
from core.notices.models import NotificationType


router = APIRouter()


class NotificationForm(BaseModel):
    notification_type: NotificationType
    title: constr(max_length=255)
    subtitle: Optional[constr(max_length=511)]
    description: Optional[constr(max_length=2047)]
    related_news_id: Optional[int]
    users_ids: Optional[list[int]]
    employees_ids: Optional[list[int]]
    couriers_ids: Optional[list[int]]
    force_with_push: Optional[bool]
    extra_push_data: Optional[dict[str, str]]
    check_newsletter: bool = True

    @root_validator(skip_on_failure=True)
    def _target_validate(cls, values: dict) -> dict:
        if all([values.get(k) is None for k in ('users_ids', 'employees_ids', 'couriers_ids')]):
            raise ValueError("Unexpected args. Target must be defined.")

        if values['notification_type'] == NotificationType.news and values.get('related_news_id') is None:
            raise ValueError("Unexpected args. 'related_news_id' must be with 'news' notification type.")

        return values


@router.post(
    "",
    description="Creates notification.",
    response_model=BaseOK,
    responses=get_response_models(
        "system_create_notification",
        exceptions=[],
        with_422_error=False,
        resp200ok=prepare_response_scheme(BaseOK)
    ),
    dependencies=[Depends(OnlyFor(for_cooperator=True, for_system=True))]
)
async def create_notification(
        form: NotificationForm,
        db=Depends(GetCurrentDB(user_is_optional=True, default_access=AccessServer.main))
) -> BaseOK:
    await notification.send_notifications(db=db, **form.dict())
    return BaseOK()
