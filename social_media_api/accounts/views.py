from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from django.contrib.auth import authenticate
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import CustomUser

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
             "user": UserSerializer(user).data,
             "token": token.key
             }, status=status.HTTP_201_CREATED)
    

class LoginView(APIView):

   def post (self, request):
       serializer = LoginSerializer(data=request.data)
       if serializer.is_valid():
             user = serializer.validated_data
             token, created = Token.objects.get_or_create(user=user)
             return Response({"token": token.key}, status=status.HTTP_200_OK)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveAPIView):
      serializer_class = UserSerializer

      def get_object(self):
            return self.request.user
      
class FollowUserView(generics.GenericAPIView):
      permission_classes = [permissions.IsAuthenticated]

      def post(self, request, user_id):
            user_to_follow = get_object_or_404(CustomUser, id=user_id)
            request.user.following.add(user_to_follow)
            return Response({"message": f"You are now following {user_to_follow.username}"},
                            status=status.HTTP_200_OK)
      
class UnfollowUserView(generics.GenericAPIView):
      permission_classes = [permissions.IsAuthenticated]

      def  post(self, request, user_id):
            user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
            request.user.following.remove(user_to_unfollow)
            return Response({"message": f"You have unfollowed {user_to_unfollow.username}"},
                            status=status.HTTP_200_OK)
     



