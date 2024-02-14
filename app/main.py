from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from core.config.internal import service_settings

from core.common.middleware import request_middleware
from core.events import create_start_app_handler, create_stop_app_handler
from core.exception import AppHTTPException
from core.exception_handler import (
    http_internal_error_handler,
    http422_error_handler,
    http_unhandled_error_handler,
    http_handled_error_handler
)
from core.logs import configure_logging
from core.logs.dependencies import log_json

from api.routes import router as api_router


app = FastAPI(dependencies=[Depends(log_json)])
configure_logging()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_event_handler(
    "startup",
    create_start_app_handler(),
)
app.add_event_handler(
    "shutdown",
    create_stop_app_handler(),
)

# todo остановился тут

app.include_router(api_router)


app.add_exception_handler(RequestValidationError, http422_error_handler)
app.add_exception_handler(AppHTTPException, http_handled_error_handler)

# обработка не штатных ошибок
app.add_exception_handler(StarletteHTTPException, http_unhandled_error_handler)
app.add_exception_handler(Exception, http_internal_error_handler)

app.add_middleware(BaseHTTPMiddleware, dispatch=request_middleware)


# if not gcs_settings.USE_GCS:
#     app.mount("/static", StaticFiles(directory="/static"), name="static")


if not service_settings.SHOW_API_DOCS:
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None
