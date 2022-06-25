from django.shortcuts import get_object_or_404

from rest_framework import serializers

from .models import ImagePost, TheFollowing


class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
        required=False
    )

    class Meta:
        model = ImagePost
        exclude = ["user", "created_at", "latest_edit"]
        # fields = "__all__"

    def create(self, validated_data):
        return ImagePost.objects.create(
            user=self.context["user"],
            **validated_data)


class UserFollowerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheFollowing
        exclude = ["created_at", "latest_edit", "id", "followed"]


class UserFollowingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheFollowing
        exclude = ["created_at", "latest_edit", "id", "follower"]


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheFollowing
        exclude = ["created_at", "latest_edit", "id"]

    def create(self, validated_data):
        follower = self.context["follower"]
        followed = validated_data["followed"]
        return TheFollowing.objects.create(follower=follower, followed=followed)
