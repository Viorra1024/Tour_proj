# config/urls.py
from django.contrib import admin
from django.urls import path, include # Убедись, что include импортирован
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- ДОБАВЬ ЭТУ СТРОКУ ---
    # Подключаем URL-адреса API из приложения tours.api
    # Префикс /api/v1/ означает, что все API эндпоинты будут начинаться с этого пути
    path('api/v1/', include('tours.api.urls')),
    # ------------------------

    # Эта строка у тебя уже есть - подключает обычные веб-страницы
    path('', include('tours.urls')),

    # Authentication URLs (оставляем как есть)
    path('accounts/login/', auth_views.LoginView.as_view(template_name='tourgid/auth/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(template_name='tourgid/auth/password_change.html'), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='tourgid/auth/password_change_done.html'), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='tourgid/auth/password_reset.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='tourgid/auth/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='tourgid/auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='tourgid/auth/password_reset_complete.html'), name='password_reset_complete'),

    # Favicon redirect (оставляем как есть)
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
]

# Add media URL in development (оставляем как есть)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)