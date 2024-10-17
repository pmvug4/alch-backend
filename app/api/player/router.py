from fastapi import APIRouter

from .views import router as self_router
from .player.views import router as player_router


router = APIRouter()

router.include_router(self_router, tags=["03_00__PlayerFull"])
router.include_router(player_router, tags=["03_01__Player"], prefix='/player')
