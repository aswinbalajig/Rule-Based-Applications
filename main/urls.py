from django.urls import path
from . import views
from rest_framework_nested import routers


router=routers.DefaultRouter()
router.register('rules',views.ruleStoreViewSet,basename='rules')

urlpatterns=[
    path('rules/<int:rule_id>/evaluate',views.ruleEvaluate.as_view(),name='rule-evaluate')
]+router.urls