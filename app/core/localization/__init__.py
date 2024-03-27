from enum import Enum
import contextvars

from .data import src


class Language(str, Enum):
    ru = 'ru'
    en = 'en'


lang_map = {
    'ru': Language.ru,
    'ru-ru': Language.ru,
    'en': Language.en,
    'en-en': Language.en
}


lang_contextvar = contextvars.ContextVar("localization_lang", default=Language.en)


def get_text(
        key: str,
        lang: Language | str,
        default: str = 'Here must be a text #todo.'
) -> str:
    if isinstance(lang, str):
        lang = lang_map.get(lang, 'en')

    return src.get(lang.value, src['en']).get(key, src['en'].get(key, default))
