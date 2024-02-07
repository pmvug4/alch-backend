from fastapi import Depends

from core.common.security import get_current_user, GetCurrentDB

from api.users.model import User

from .models import *
from . import store


async def get_preferences(
        db=Depends(GetCurrentDB()),
        user: User = Depends(get_current_user)
) -> Preferences:
    if user.preferences_id:
        return await store.get_preference(db, pk=user.preferences_id)
    else:
        preferences = await store.create_preferences(db, user_id=user.user_id)
        user.preferences_id = preferences.id
        return preferences
