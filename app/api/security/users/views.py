from fastapi import Depends, APIRouter
from databases.core import Connection

from core.schemas import get_response_models, prepare_response_scheme
from core.db import get_db

from logic.security import depends
from logic.security.users import UserView, User

router = APIRouter()


@router.get(
    "/me",
    description="Get my user",
    response_model=UserView,
    responses=get_response_models(
        "get_my_user",
        [],
        with_422_error=False,
        resp200ok=prepare_response_scheme(UserView)
    )
)
async def get_my_user(
        user: User = Depends(depends.GetCurrentUser())
) -> UserView:
    return user
