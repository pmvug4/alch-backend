from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunStateSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    TELEGRAM_DB_ALARM_EXEC_THRESHOLD: bool = Field(
        True,
        validation_alias='TELEGRAM_DB_ALARM_EXEC_THRESHOLD',
        description="Флаг, будут ли отслеживаться медленные запросы в БД, и отправляться в телеграм"
    )
    TELEGRAM_DB_ALARM_EXEC_THRESHOLD_MS: int = Field(
        1500,
        validation_alias='TELEGRAM_DB_ALARM_EXEC_THRESHOLD_TIME',
        description="Минимальное время выполнения, после которого будет оповещение"
    )

    TELEGRAM_PUSH_REPORTS_ENABLED: bool = Field(
        False,
        validation_alias='TELEGRAM_PUSH_REPORTS_ENABLED',
        description="Флаг, будет ли лог пушей дублироваться в телеграм"
    )

    TELEGRAM_SERVICE_ALARM_EXEC_THRESHOLD: bool = Field(
        True,
        validation_alias='TELEGRAM_SERVICE_ALARM_EXEC_THRESHOLD',
        description="Флаг, будут ли отслеживаться медленные запросы, и оптравляться в телеграм"
    )
    TELEGRAM_SERVICE_ALARM_EXEC_THRESHOLD_MS: int = Field(
        1500,
        validation_alias='TELEGRAM_SERVICE_ALARM_EXEC_THRESHOLD_MS',
        description="Минимальное время выполнения, после которого будет оповещение"
    )

    SENT_EMAILS_IN_TELEGRAM: bool = Field(
        True,
        validation_alias='SENT_EMAILS_IN_TELEGRAM',
        description="Показывает, активен ли SMTP мок"
    )


run_state_settings = RunStateSettings()
