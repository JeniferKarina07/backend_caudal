from django.urls import path

from .views import (
    AlertsView,
    DashboardView,
    FlowReadingListCreateView,
    LatestFlowReadingView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('v1/readings/', FlowReadingListCreateView.as_view(), name='flow-readings'),
    path('v1/readings/latest/', LatestFlowReadingView.as_view(), name='flow-reading-latest'),
    path('v1/dashboard/', DashboardView.as_view(), name='flow-dashboard'),
    path('v1/alerts/', AlertsView.as_view(), name='flow-alerts'),
]
