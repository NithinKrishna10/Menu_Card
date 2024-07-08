from fastapi import APIRouter

from .login import router as login_router
from .logout import router as logout_router
from .posts import router as posts_router
from .rate_limits import router as rate_limits_router
from .tasks import router as tasks_router
from .tiers import router as tiers_router
from .users import router as users_router
from .category import router as category_router
from .product import router as product_router
from .menu_card import router as menu_card_router
from .advertisement import router as advertisement_router
from .leads import router as leads_router

router = APIRouter(prefix="/v1")
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(users_router)
router.include_router(category_router)
router.include_router(product_router)
router.include_router(menu_card_router)
router.include_router(advertisement_router)
router.include_router(leads_router)
# router.include_router(tasks_router)
# router.include_router(tiers_router)
# router.include_router(rate_limits_router)
