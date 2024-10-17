from django.urls import path
from . import views
from rest_framework_nested import routers


router=routers.DefaultRouter()
router.register('rules',views.ruleStoreViewSet,basename='rules')
urlpatterns=router.urls