from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from .views import (
    UserViewSet, DestinationViewSet, HotelViewSet, AttractionViewSet,
    ReviewViewSet, ExcursionViewSet, BookingViewSet, GuideViewSet, FavoriteViewSet
)

# Create a schema view for Swagger documentation
schema_view = get_schema_view(
    openapi.Info(
        title="TourGid API",
        default_version='v1',
        description="API for TourGid - Directory of Tourist application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@tourgid.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Initialize the router
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'destinations', DestinationViewSet)
router.register(r'hotels', HotelViewSet)
router.register(r'attractions', AttractionViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'excursions', ExcursionViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'guides', GuideViewSet, basename='guide')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'favorites', FavoriteViewSet)

urlpatterns = [
    # API routes
    path('', include(router.urls)),
    
    # JWT Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # DRF auth
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
