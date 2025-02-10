from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from tasks.views import FileModelViewSet
from users.views import LoginView, LogoutView, MeViewSet, NotificationView, UserViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="App API",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    url=settings.APP_API_HOST,
)

router = routers.SimpleRouter()
router.register('users', UserViewSet)
router.register('files', FileModelViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/me/', ensure_csrf_cookie(MeViewSet.as_view({'get': 'retrieve'}))),
    path('api/auth/login/', LoginView.as_view()),
    path('api/auth/logout/', LogoutView.as_view()),
    path('api/notifications/', NotificationView.as_view()),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()