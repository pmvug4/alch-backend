from fastapi import APIRouter, Depends

from core.exception import IncorrectCredentials
from core.schemas import get_response_models, prepare_response_scheme
from core.common.security import GetCurrentDB

from . import depends
from . import store
from .exceptions import *
from .models import *

router = APIRouter(tags=['preferences'])

_base_exc = [IncorrectCredentials]


@router.get(
    "",
    description="Returns user preferences.",
    response_model=Preferences,
    responses=get_response_models(
        "get_user_preferences",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(Preferences)
    )
)
async def get_preferences(
        preferences: Preferences = Depends(depends.get_preferences)
):
    return preferences


@router.post(
    "/news/disable",
    description="Disables user news receiving option.",
    response_model=Preferences,
    responses=get_response_models(
        "disable_user_news",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(Preferences)
    )
)
async def disable_user_news(
        db=Depends(GetCurrentDB()),
        preferences: Preferences = Depends(depends.get_preferences)
):
    if not preferences.news_enabled:
        return preferences

    return await store.update_news_enabled(db, pk=preferences.id, value=False)


@router.post(
    "/news/enable",
    description="Enables user news receiving option.",
    response_model=Preferences,
    responses=get_response_models(
        "enable_user_news",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(Preferences)
    )
)
async def enable_user_news(
        db=Depends(GetCurrentDB()),
        preferences: Preferences = Depends(depends.get_preferences)
):
    if preferences.news_enabled:
        return preferences

    return await store.update_news_enabled(db, pk=preferences.id, value=True)


@router.post(
    "/news/switch",
    description="Switches user news receiving option.",
    response_model=Preferences,
    responses=get_response_models(
        "switch_user_news",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(Preferences)
    )
)
async def switch_user_news(
        db=Depends(GetCurrentDB()),
        preferences: Preferences = Depends(depends.get_preferences)
):
    return await store.update_news_enabled(db, pk=preferences.id, value=not preferences.news_enabled)


@router.post(
    "/push/disable",
    description="Disables user push receiving option.",
    response_model=Preferences,
    responses=get_response_models(
        "disable_user_push",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(Preferences)
    )
)
async def disable_user_push(
        db=Depends(GetCurrentDB()),
        preferences: Preferences = Depends(depends.get_preferences)
):
    if not preferences.push_enabled:
        return preferences

    return await store.update_push_enabled(db, pk=preferences.id, value=False)


@router.post(
    "/push/enable",
    description="Enables user push receiving option.",
    response_model=Preferences,
    responses=get_response_models(
        "enable_user_push",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(Preferences)
    )
)
async def enable_user_push(
        db=Depends(GetCurrentDB()),
        preferences: Preferences = Depends(depends.get_preferences)
):
    if preferences.push_enabled:
        return preferences

    return await store.update_push_enabled(db, pk=preferences.id, value=True)


@router.post(
    "/push/switch",
    description="Switches user push receiving option.",
    response_model=Preferences,
    responses=get_response_models(
        "switch_user_push",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(Preferences)
    )
)
async def switch_user_push(
        db=Depends(GetCurrentDB()),
        preferences: Preferences = Depends(depends.get_preferences)
):
    return await store.update_push_enabled(db, pk=preferences.id, value=not preferences.push_enabled)


@router.post(
    "/sms/disable",
    description="Disables user SMS receiving option.",
    response_model=Preferences,
    responses=get_response_models(
        "disable_user_sms",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(Preferences)
    )
)
async def disable_user_sms(
        db=Depends(GetCurrentDB()),
        preferences: Preferences = Depends(depends.get_preferences)
):
    if not preferences.sms_enabled:
        return preferences

    return await store.update_sms_enabled(db, pk=preferences.id, value=False)


@router.post(
    "/sms/enable",
    description="Enables user SMS receiving option.",
    response_model=Preferences,
    responses=get_response_models(
        "enable_user_sms",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(Preferences)
    )
)
async def enable_user_sms(
        db=Depends(GetCurrentDB()),
        preferences: Preferences = Depends(depends.get_preferences)
):
    if preferences.sms_enabled:
        return preferences

    return await store.update_sms_enabled(db, pk=preferences.id, value=True)


@router.post(
    "/sms/switch",
    description="Switches user SMS receiving option.",
    response_model=Preferences,
    responses=get_response_models(
        "switch_user_sms",
        exceptions=_base_exc,
        with_422_error=False,
        resp200ok=prepare_response_scheme(Preferences)
    )
)
async def switch_user_sms(
        db=Depends(GetCurrentDB()),
        preferences: Preferences = Depends(depends.get_preferences)
):
    return await store.update_sms_enabled(db, pk=preferences.id, value=not preferences.sms_enabled)
