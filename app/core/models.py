

class FormattedDict:
    def __init__(self, dictionary: dict[..., str | None]):
        self._dict = dictionary

    def format(self, **kwargs) -> dict:
        return {k: (v.format(**kwargs) if isinstance(v, str) else v) for k, v in self._dict.items()}
