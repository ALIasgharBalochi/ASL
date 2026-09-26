from rest_framework.routers import DefaultRouter
from .views.core_views import (
    CategoryViewSet,
    ProcessViewSet,
)

router = DefaultRouter()

router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"processes", ProcessViewSet, basename="process")




urlpatterns = router.urls