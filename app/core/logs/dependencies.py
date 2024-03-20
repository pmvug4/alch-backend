from fastapi import Request
from contextlib import suppress

from core.logs import log


async def log_request(
        request: Request,
):
    _msg = f"Request: [{request.method}] -> {request.url} < {request.headers} << {request.path_params}"
    with suppress(Exception):
        _msg += f" <<< {await request.json()}"
    log.info(_msg)
