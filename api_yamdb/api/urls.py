from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserRegistrationView,
                    UserTokenObtainView, UserViewSet)

app_name = "api"


router = routers.DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("categories", CategoryViewSet, basename="categories")
router.register("genres", GenreViewSet, basename="genres")
router.register("titles", TitleViewSet, basename="titles")
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)


urlpatterns = [
    path("v1/auth/signup/", UserRegistrationView.as_view(), name="register"),
    path("v1/auth/token/", UserTokenObtainView.as_view(), name="token_create"),
    path("v1/", include(router.urls)),
]
