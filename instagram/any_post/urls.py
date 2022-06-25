from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import ExplorerViewSet, PersonalPostList, PersonalPostDetail, Profile, FollowerCRUD

router = DefaultRouter()
router.register("explorer", ExplorerViewSet, basename="all_posts")
router.register("follow", FollowerCRUD, basename="follow")


urlpatterns = [
    path("my-posts/", PersonalPostList.as_view(), name="my_posts"),
    path("my-posts/<int:pk>", PersonalPostDetail.as_view(), name="my_posts_detail"),
    path("profile/<int:pk>", Profile.as_view(), name="profile"),
] + router.urls

