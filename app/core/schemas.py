from collections import defaultdict
from typing import Union, List, Any

from pydantic import BaseModel, create_model

from core.common import strings


class BaseResponse(BaseModel):
    error: None = None


class BaseOK(BaseModel):
    response: str = "OK"


class BaseFileOK(BaseOK):
    len: int


class _Error422Schema(BaseModel):
    error_msg: str = strings.validation_error
    error_name: str = "parsedataerror"
    error_payload: dict = dict()

class Error422Schema(BaseModel):
    data: None =  None
    error: _Error422Schema


models_prefixes = []


def get_response_models(prefix, exceptions: List[Any], with_422_error=True, resp200ok=None) -> dict:
    """
     Получает список exception типа AppHTTPException/
     на основании переменных класса формирует ответ который будет в случае данной ошибок и
     формирует словарь для responses с указанием всех возможных вариантов error для данного status_code
    """
    if prefix in models_prefixes:
        raise Exception(f"You cannot declare different models with the same name = {prefix}. OpenAPI won't work")
    else:
        models_prefixes.append(prefix)

    error_by_code = defaultdict(list)

    for e in exceptions:
        #группируем все модели для данного типа ошибки
        error_by_code[e.http_code].append(e.get_model())

    res = dict()
    for k, v in error_by_code.items():
        res[k] = {"model": create_model(f"{prefix}_errors{k}", error=(Union[tuple(v)], None))}
    if with_422_error:
        res[422] = {"model": Error422Schema}
    if resp200ok:
        res[200] = {"model": resp200ok}

    return res


response_models = dict()
def prepare_response_scheme(response_model):
    """
     т.к. мы оборачиваем ответ в middleware нам нужно подготовить такуюже схему.
     это необходимо для генерации документации
    """
    exist_model = response_models.get(f"_{response_model.__name__}")
    if exist_model:
        return exist_model
    model = create_model(f"_{response_model.__name__}", error=(type(None), None), data=(response_model,...))
    response_models[f"_{response_model.__name__}"] = model
    return model