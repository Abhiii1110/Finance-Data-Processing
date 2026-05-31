from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserViewSet, FinancialRecordViewSet, DashboardView

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('records', FinancialRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]