from fastapi import APIRouter

from .player.views import router as player_router


router = APIRouter()

router.include_router(player_router, tags=["03__Player"], prefix='/player')
