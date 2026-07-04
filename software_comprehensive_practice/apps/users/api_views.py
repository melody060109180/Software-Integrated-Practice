from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Profile, Address
from .serializers import (
    UserSerializer, ProfileSerializer, AddressSerializer,
    LoginSerializer, RegisterSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                login(request, user)
                return Response({
                    'success': True,
                    'user': UserSerializer(user).data,
                    'message': '登录成功'
                })
            return Response({
                'success': False,
                'message': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            'success': False,
            'message': str(serializer.errors)
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return Response({
                'success': True,
                'user': UserSerializer(user).data,
                'message': '注册成功'
            }, status=status.HTTP_201_CREATED)
        error_list = []
        for field, msgs in serializer.errors.items():
            if isinstance(msgs, list):
                error_list.extend(msgs)
            else:
                error_list.append(str(msgs))
        return Response({
            'success': False,
            'message': '; '.join(error_list)
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'success': True, 'message': '已退出登录'})


@method_decorator(csrf_exempt, name='dispatch')
class ProfileAPI(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


@method_decorator(csrf_exempt, name='dispatch')
class AddressListAPI(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class AddressDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
