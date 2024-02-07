from fastapi import APIRouter

from core.common import strings
from core.schemas import prepare_response_scheme, get_response_models

router = APIRouter()


@router.get(
    "/agreement",
    description="Returns agreement strings.",
    response_model=list[str],
    responses=get_response_models(
        "agreement",
        exceptions=[],
        with_422_error=False,
        resp200ok=prepare_response_scheme(list[str])
    )
)
async def agreement(strings_length: int = 8) -> list[str]:
    return strings.agreement_contract_content[:strings_length]
