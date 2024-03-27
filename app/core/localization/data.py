

src = {
    'ru': {
        'error__authorization_error': "Произошла ошибка авторизации.",
        'error__user_creation_error': "Произошла ошибка при создании пользователя."
    },
    'en': {
        'error__authorization_error': "Authorization error.",
        'error__user_creation_error': "Something went wrong while user creation."
    }
}


def add_localization_value(
        key: str,
        **lang_to_values
) -> None:
    for lang, value in lang_to_values.items():
        src[lang][key] = value


def error_add_localization(
        error_name: str,
        **lang_to_values
) -> None:
    return add_localization_value(
        f'error__{error_name}',
        **lang_to_values
    )
