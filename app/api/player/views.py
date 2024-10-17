from fastapi import Depends, APIRouter

from core.schemas import get_response_models, prepare_response_scheme

from logic.player import depends, PlayerFull

router = APIRouter()


@router.get(
    '/',
    description="Get my player full",
    response_model=PlayerFull,
    responses=get_response_models(
        "get_my_player_full",
        [],
        with_422_error=False,
        resp200ok=prepare_response_scheme(PlayerFull)
    )
)
async def get_my_player_full(
        player: PlayerFull = Depends(depends.GetCurrentPlayerFull())
) -> PlayerFull:
    return player
