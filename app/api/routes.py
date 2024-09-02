from fastapi import APIRouter

from .security.router import router as security_router
from .player.router import router as player_router


router = APIRouter(prefix='/api/v1')

router.include_router(security_router, prefix='/security')
router.include_router(player_router, prefix='/player')
