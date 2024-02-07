from enum import Enum
from typing import Optional

from pydantic import BaseSettings, Field


class RunStates(Enum):
    LOCAL = 1
    DEBUG = 2
    PP = 3
    PROD = 4


run_state_map = {
    1: RunStates.LOCAL,
    2: RunStates.DEBUG,
    3: RunStates.PP,
    4: RunStates.PROD
}

log_level = {
    1: "DEBUG",
    2: "INFO",
    3: "ERROR"
}

default_log_path = {RunStates.LOCAL: ".\\logs\\",
                    RunStates.DEBUG: "/app/logs/",
                    RunStates.PP: "/app/logs/",
                    RunStates.PROD: "/app/logs/",
                    }


class CommonSettings(BaseSettings):
    SERVICE_NAME: str = Field("QWQER", env="SERVICE_NAME")
    API_KEY: str = Field(..., env="API_KEY")
    TESTING_KEY: Optional[str] = Field(None, env='TESTING_KEY')

    STATE: int = Field(RunStates.LOCAL.value, env='RUN_STATE')
    LOG_PATH: str = Field(None, env="LOG_PATH")
    LOG_STDOUT: bool = Field(True, env='LOG_STDOUT')
    LOG_FILE_LEVEL: str = Field('INFO', env='LOG_FILE_LEVEL')
    LOG_STDOUT_LEVEL: str = Field('DEBUG', env='LOG_STDOUT_LEVEL')
    LOG_SERIALIZE: bool = Field(True, env='LOG_SERIALIZE')
    TIME_BEFORE_TG_ALARM: int = Field(1500, env="TIME_BEFORE_TG_ALARM")

    AUTH_ALG: str = "HS256"
    AUTH_REFRESH_TOKEN_EXPIRE_IN: int = 3600 * 24 * 30
    AUTH_ACCESS_TOKEN_EXPIRE_IN_SECONDS: int = Field(3600, env="AUTH_ACCESS_TOKEN_EXPIRE_IN_SECONDS")
    AUTH_SECRET: str = Field(..., env="AUTH_SECRET")
    AUTH_OTP_PASSWORD_VALID_PERIOD_SECONDS: int = Field(..., env="AUTH_OTP_PASSWORD_VALID_PERIOD_SECONDS")
    AUTH_OTP_PASSWORD_CHECKS: int = Field(3, env="AUTH_OTP_PASSWORD_CHECKS")
    AUTH_OTP_RETRY_PERIOD_SECONDS: int = Field(300, env="AUTH_OTP_RETRY_PERIOD_SECONDS")
    AUTH_OTP_PASSWORD_LENGTH = 6
    AUTH_BY_COOKIE: bool = Field(False, env='AUTH_BY_COOKIE')

    SENT_SMS_BY_TELEGRAM: bool = Field(True, env='MESSAGE_SENT_BY_TELEGRAM')
    USE_PHONE_PROXY: bool = Field(False, env='USE_PHONE_PROXY')

    AUTOCOMPLETE_DELIVERY_INTERVAL: int = Field(3600 * 3, env='AUTOCOMPLETE_DELIVERY_INTERVAL')

    # Базовая погрешность в секундах на точку доставки
    BASE_ROUTE_POINT_ERROR: int = Field(180, env='BASE_ROUTE_POINT_ERROR')
    # Дополнительное время в секундах на каждую промежуточную точку маршрута
    ROUTE_INTERMEDIATE_POINT_ACTION_TIME: int = Field(900, env='ROUTE_INTERMEDIATE_POINT_ACTION_TIME')

    ROUTE_POINT_SECURITY_CODE_REARM_SECONDS: int = Field(60, env='ROUTE_POINT_SECURITY_CODE_REARM_SECONDS')
    ROUTE_POINT_SECURITY_CODE_ALIVE_SECONDS: int = Field(180, env='ROUTE_POINT_SECURITY_CODE_ALIVE_SECONDS')
    ROUTE_MAX_ARRIVAL_POINTS: int = Field(5, env='ROUTE_MAX_ARRIVAL_POINTS')
    GOOGLEMAPS_API_KEY: str = Field(..., env='GOOGLEMAPS_API_KEY')
    GOOGLE_APPLICATION_CREDENTIALS_COURIER: str = Field(
        ...,
        env='GOOGLE_APPLICATION_CREDENTIALS_COURIER',
        description="path to file"
    )
    GOOGLE_APPLICATION_CREDENTIALS_CUSTOMER: str = Field(
        ...,
        env='GOOGLE_APPLICATION_CREDENTIALS_CUSTOMER',
        description="path to file"
    )

    @property
    def RUN_STATE(self):
        return run_state_map[self.STATE]

    @property
    def log_filename_full_path(self):
        return f"{self.LOG_PATH or default_log_path[self.RUN_STATE]}{self.SERVICE_NAME}.log"

    @property
    def HTTP_EXTRA_INFO(self):
        state = self.RUN_STATE in (RunStates.LOCAL, RunStates.DEBUG, RunStates.PP)
        return state


common_settings = CommonSettings()
