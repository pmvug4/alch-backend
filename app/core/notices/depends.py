from fastapi import Depends

from .models import *
from . import store

from core.common.security import get_current_user, GetCurrentDB

from api.users.model import User


async def get_receiver(
        db=Depends(GetCurrentDB()),
        user: User = Depends(get_current_user)
) -> NoticeReceiver:
    async with db.transaction():
        receiver = await store.NoticeReceiver.get(db, user_id=user.user_id, return_none=True, for_update=True)
        if not receiver:
            receiver = await store.NoticeReceiver.create(db, NoticeReceiverForm(user_id=user.user_id))

        return receiver
