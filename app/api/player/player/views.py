from fastapi import Depends, APIRouter

from core.schemas import get_response_models, prepare_response_scheme

from logic.player import depends, Player

router = APIRouter()


@router.get(
    "/",
    description="Get my player",
    response_model=Player,
    responses=get_response_models(
        "get_my_player",
        [],
        with_422_error=False,
        resp200ok=prepare_response_scheme(Player)
    )
)
async def get_my_player(
        player: Player = Depends(depends.GetCurrentPlayer())
) -> Player:
    return player
