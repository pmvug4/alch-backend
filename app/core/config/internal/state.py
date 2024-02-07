from pydantic import BaseSettings, Field


class RunStateSettings(BaseSettings):
    TELEGRAM_DB_ALARM_EXEC_THRESHOLD: bool = Field(
        True,
        env='TELEGRAM_DB_ALARM_EXEC_THRESHOLD',
        description="Флаг, будут ли отслеживаться медленные запросы в БД, и отправляться в телеграм"
    )
    TELEGRAM_DB_ALARM_EXEC_THRESHOLD_MS: int = Field(
        1500,
        env='TELEGRAM_DB_ALARM_EXEC_THRESHOLD_TIME',
        description="Минимальное время выполнения, после которого будет оповещение"
    )

    TELEGRAM_PUSH_REPORTS_ENABLED: bool = Field(
        False,
        env='TELEGRAM_PUSH_REPORTS_ENABLED',
        description="Флаг, будет ли лог пушей дублироваться в телеграм"
    )

    TELEGRAM_SERVICE_ALARM_EXEC_THRESHOLD: bool = Field(
        True,
        env='TELEGRAM_SERVICE_ALARM_EXEC_THRESHOLD',
        description="Флаг, будут ли отслеживаться медленные запросы, и оптравляться в телеграм"
    )
    TELEGRAM_SERVICE_ALARM_EXEC_THRESHOLD_MS: int = Field(
        1500,
        env='TELEGRAM_SERVICE_ALARM_EXEC_THRESHOLD_MS',
        description="Минимальное время выполнения, после которого будет оповещение"
    )

    SENT_EMAILS_IN_TELEGRAM: bool = Field(
        True,
        env='SENT_EMAILS_IN_TELEGRAM',
        description="Показывает, активен ли SMTP мок"
    )
