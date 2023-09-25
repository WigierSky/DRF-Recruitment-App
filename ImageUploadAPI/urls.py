from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views

from images import views

router = DefaultRouter()
router.register(r"images", views.ImageViewSet)
router.register(r"users", views.UserProfileViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    path("api/token/", obtain_auth_token, name="api_token"),
    path("upload_image/", views.upload_image, name="upload_image"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("media/thumbnails/<str:thumbnail_name>/",views.thumbnail_view,name="thumbnail_view"),
    path("media/images/<str:image_name>/expires_in=<str:expires_in_str>/", views.expire_link, name="expiring_image"),
    path("media/images/<str:image_name>/", views.image_view, name="original_image"),
]
