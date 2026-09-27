from rest_framework.routers import DefaultRouter
from .views.core_views import (
    CategoryViewSet,
    ProcessViewSet,
)
from .views.form_views import FormViewSet, QuestionViewSet, QuestionOptionViewSet

router = DefaultRouter()

router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"processes", ProcessViewSet, basename="process")
router.register(r"forms", FormViewSet, basename="form")
router.register(r"questions", QuestionViewSet, basename="question")
router.register(r"question-options", QuestionOptionViewSet, basename="question-option")



urlpatterns = router.urls