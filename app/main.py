import uvicorn
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from core.common.middleware import request_middleware
from core.config.common import common_settings, RunStates
from core.config.gcs import gcs_settings
from core.events import create_start_app_handler, create_stop_app_handler
from core.exception import AppHTTPException
from core.exception_handler import error_exception_handler, http422_error_handler, http_error_handler, \
    http_unhadlederror_handler
from core.logs import configure_logging
from core.logs.dependencies import log_json

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
app.include_router(api_router)

app.add_exception_handler(RequestValidationError, http422_error_handler)
app.add_exception_handler(AppHTTPException, http_error_handler)

# обработка не штатных ошибок
app.add_exception_handler(StarletteHTTPException, http_unhadlederror_handler)
app.add_exception_handler(Exception, error_exception_handler)
app.add_middleware(BaseHTTPMiddleware, dispatch=request_middleware)

if not gcs_settings.USE_GCS:
    app.mount("/static", StaticFiles(directory="/static"), name="static")

if common_settings.STATE == RunStates.PROD:
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8144)
