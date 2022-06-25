from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import authentication, permissions
from rest_framework import status
from rest_framework import generics
from rest_framework.decorators import action

from .serializers import PostSerializer, UserFollowerListSerializer, UserFollowingListSerializer, FollowSerializer
from .models import ImagePost, TheFollowing


class PersonalPostList(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = ImagePost.objects.filter(user__exact=request.user).order_by("-created_at")
        serializer = PostSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={"user": request.user})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "message": "New Post's LIT!!!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)


# class FollowersList(APIView):
#     authentication_classes = [authentication.TokenAuthentication]
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, pk):
#         qs = TheFollowing.objects.get(followed__id=pk, follower=request.user)
#         user1 = User.objects.get(id=pk)
#         if qs:
#             return HttpResponse(f"You've already followed {pk}")
#         serializer = FollowersSerializer(data=request.data, context={"user": request.user, "user1": user1})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#
#     def get(self, request, pk):
#         qs = TheFollowing.objects.filter(followed__id=pk)
#         serializer = FollowersSerializer(qs, many=True, context={"request": request})
#         return Response(serializer.data)
#

class Profile(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        qs_followers = TheFollowing.objects.filter(followed__id=pk, status="a").count()
        qs_following = TheFollowing.objects.filter(follower__id=pk, status="a").count()
        return JsonResponse({"following": qs_following, "followers": qs_followers}, safe=False)

    def post(self, request, pk=None):
        qs = get_object_or_404(User, pk=pk)
        serializer = FollowSerializer(data=request.data, context={"follower": request.user, "followed": qs})
        if qs == request.user:
            return Response(status=403)
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        else:
            return Response(serializer.errors)


# class FollowingsList(APIView):
#     def get(self, request, pk):
#         qs = TheFollowing.objects.filter(follower__id=pk)
#         serializer = FollowersSerializer(qs, many=True, context={"request": request})
#         return Response(serializer.data)


class PersonalPostDetail(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = ImagePost.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ExplorerViewSet(viewsets.ViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        qs = ImagePost.objects.filter(user=request.user).order_by("-created_at")
        serializer = PostSerializer(qs, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        qs = get_object_or_404(ImagePost, id=pk)
        serializer = PostSerializer(qs)
        return Response(serializer.data)


# *******************
class FollowerCRUD(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def list(self, request):
        qs = TheFollowing.objects.filter(followed=request.user, status="a")
        serializer = UserFollowerListSerializer(qs, many=True)
        return Response(serializer.data)

    # def create(self, request):
    #     seriailizer = FollowerSerializer(data=request.data, context={"user_darkhast_dahande": request.user})
    #     if seriailizer.is_valid():
    #         seriailizer.save()
    #         return Response(status=201)
    #     else:
    #         return Response(serialize.errors)

    @action(methods=["GET"], detail=False, url_path="user-following-list")
    def user_following_list(self, request):
        qs = TheFollowing.objects.filter(follower=request.user, status="a")
        serializer = UserFollowingListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(methods=["POST"], detail=False, url_path="follow-request/<int:pk>")
    def follow_request(self, request, pk):
        qs = settings.AUTH_USER_MODEL.get(user__pk=pk)
        serializer = FollowSerializer(data=request.data, context={"follower": request.user, "followed": qs})
        if serializer.is_valid():
            serializer.save()
            return Response(status=201)
        else:
            return Response(serializer.errors)

    @action(methods=["GET"], detail=False, url_path="pending-list")
    def pending_list(self, request):
        qs = TheFollowing.objects.filter(follower=request.user, status="p")
        serializer = UserFollowingListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True, url_path="accept-request")
    def accept_request(self, request, pk=None):
        user_follower = get_object_or_404(User, pk=pk)
        qs = get_object_or_404(TheFollowing, follower=user_follower, followed=request.user)
        if user_follower == request.user:
            return Response(status=403)
        qs.status = "a"
        qs.save()
        return Response(status=200)

    @action(methods=["POST"], detail=True, url_path="reject-unfollow")
    def reject_unfollow(self, request, pk=None):
        user_follower = get_object_or_404(User, pk=pk)
        qs = get_object_or_404(TheFollowing, follower=user_follower, followed=request.user)
        if user_follower == request.user:
            return Response(status=403)
        qs.delete()
        return Response(status=204)
