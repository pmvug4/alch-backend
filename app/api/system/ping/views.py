import asyncio

from fastapi import Depends, APIRouter, HTTPException
from starlette.status import HTTP_502_BAD_GATEWAY

from core.common.security import OnlyFor

router = APIRouter()


@router.get(
    "",
    description="Проверка работоспособности сервиса"
)
async def get():
    return {"data": "OK"}


@router.get("/time_err", dependencies=[Depends(OnlyFor(for_cooperator=True, for_system=True))])
async def raise_time_err():
    await asyncio.sleep(7)
    return {"data": "OK"}


@router.get("/alarm_err", dependencies=[Depends(OnlyFor(for_cooperator=True, for_system=True))])
async def raise_alarm_err():
    raise RuntimeError
