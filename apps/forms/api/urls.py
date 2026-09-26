from rest_framework.routers import DefaultRouter
from .views.core_views import (
    CategoryViewSet,
    ProcessViewSet,
    
)
from .views.form_views import FormViewSet

router = DefaultRouter()

router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"processes", ProcessViewSet, basename="process")
router.register(r"forms", FormViewSet, basename="form")




urlpatterns = router.urls