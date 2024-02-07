from copy import deepcopy
from ..context import request_ip_context
from fastapi import Request
from loguru import logger


async def log_json(request: Request):
    """
    Сохраняет в лог информацию о каждом входящем запросе
    """

    main_info = f"({request_ip_context.get()}) Request: [{request.method}] -> {request.url} >>> {request.headers} <<<"

    try:
        request_json = deepcopy(await request.json())
        logger.info(f"{main_info} {request_json}")
    except:
        logger.info(f"{main_info} {request.path_params}")
