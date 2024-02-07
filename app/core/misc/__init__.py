from typing import Optional


def make_fullname(
        name: Optional[str],
        middle_name: Optional[str],
        surname: Optional[str],
        default: Optional[str] = None
) -> Optional[str]:
    return ' '.join([x for x in (name, middle_name, surname) if x is not None]) or default
