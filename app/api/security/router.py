from fastapi import APIRouter

from .auth.views import router as auth_router
from .users.views import router as users_router


router = APIRouter()

router.include_router(auth_router, tags=["01__Auth"], prefix='/auth')
router.include_router(users_router, tags=["02__Users"], prefix='/users')
