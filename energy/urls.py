from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'grids', views.GridViewSet)
router.register(r'regions', views.GridRegionViewSet)
router.register(r'nodes', views.GridNodeViewSet)
router.register(r'measures', views.MeasuresViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('measures/query/', views.MeasuresAPIView.as_view(), name='measures-query'),
    path('measures/evolution/', views.MeasuresEvolutionAPIView.as_view(), name='measures-evolution'),
    path('dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),
] 