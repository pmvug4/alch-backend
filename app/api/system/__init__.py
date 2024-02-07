from fastapi import APIRouter
from .cooperators import router as cooperators_router
from .notifications import router as notifications_router
from .ping.views import router as ping_router
from .resources import router as resources_router

router = APIRouter(tags=['system'])
router.include_router(cooperators_router, prefix='/cooperators')
router.include_router(notifications_router, prefix='/notifications')
router.include_router(ping_router, prefix='/ping')
router.include_router(resources_router, prefix='/resources')
