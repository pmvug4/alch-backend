from fastapi import APIRouter, Depends
#
# from core.common.security import OnlyFor
#
# from api.account.views import router as intercomrouter
# from api.auth.views import router as authrouter
# from api.users.views import router as userrouter
# from api.bases import router as bases_router
# from api.couriers import router as courier_router
# from api.webhooks import router as webhook_router
# from api.preferences import router as preferences_router
# from api.debug import router as debug_router
# from api.customer import router as customer_router
# from api.notices import router as notices_router
# from api.search import router as search_router
# from api.cooperators import router as cooperator_router
# from api.system import router as system_router
# from api.testing import router as testing_router
# from api.faq import router as faq_router
# from api.landings import router as landings_router
#
#

from .security.router import router as security_router



router = APIRouter(prefix='/api/v1')

router.include_router(security_router, prefix='/security')


# router.include_router(intercomrouter, prefix="/api/v1/account", tags=['Account'])
# router.include_router(authrouter, prefix="/api/v1/auth")
# router.include_router(userrouter, prefix="/api/v1/users")
#
# router.include_router(
#     customer_router,
#     prefix="/api/v1/customer",
#     dependencies=[Depends(OnlyFor(for_customer=True))]
# )
#
# router.include_router(
#     courier_router,
#     prefix="/api/v1/courier",
#     dependencies=[Depends(OnlyFor(for_courier=True))]
# )
#
# router.include_router(
#     cooperator_router,
#     prefix="/api/v1/cooperator",
#     dependencies=[Depends(OnlyFor(for_cooperator=True))]
# )
#
# router.include_router(system_router, prefix="/api/v1/system")
# router.include_router(testing_router, prefix="/api/v1/testing")
#
# router.include_router(bases_router, prefix="/api/v1/bases")
# router.include_router(notices_router, prefix="/api/v1/notices")
# router.include_router(webhook_router, prefix="/api/v1/webhooks")
# router.include_router(preferences_router, prefix="/api/v1/preferences")
# router.include_router(search_router, prefix="/api/v1/search")
# router.include_router(debug_router, prefix="/api/v1/debug")
# router.include_router(faq_router, prefix="/api/v1/faq")
# router.include_router(landings_router, prefix="/api/v1/landings")
