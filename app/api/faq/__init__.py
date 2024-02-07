from fastapi import APIRouter, Depends

from core.common.security import get_current_user, GetCurrentDB
from core.cooperators.exceptions import CooperatorDoesNotExist
from core.exception import AccessForbiden, IncorrectCredentials
from core.faq.models import FaqList, Role
from core.faq.services import assert_role_faq
from core.schemas import get_response_models, prepare_response_scheme

from api.users.model import User

from ..account.model import PlatformType

router = APIRouter(tags=["faq"])
_base_exc = [
    IncorrectCredentials,
    AccessForbiden,
    CooperatorDoesNotExist
]


@router.get(
    "/list",
    description="Returns FAQ list.",
    response_model=FaqList,
    responses=get_response_models(
        "get_faq_list",
        exceptions=[*_base_exc],
        with_422_error=False,
        resp200ok=prepare_response_scheme(FaqList)
    )
)
async def get_faq_list(
        role: Role,
        platform: PlatformType = None,
        user: User = Depends(get_current_user),
        page_size: int = 20,
        page_number: int = 1,
        db=Depends(GetCurrentDB())
) -> FaqList:
    await assert_role_faq(db, user, role)
    return await FaqList.db_get(db, platform=platform, role=role, page_size=page_size,
                                page_number=page_number)
