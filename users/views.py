from django.shortcuts import render
from django.http import JsonResponse
from .models import UserProfile,User
from .serializers import UserProfileSerializer,UserSerializer
from rest_framework import viewsets,generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core import exceptions as django_exceptions
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
import logging

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
 
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return JsonResponse(serializer.data)
    
class RegisterView(APIView):
    """
    Регистрация пользователя.
    Ожидает POST JSON:
    {
      "email": "user@example.com",
      "password": "secret123",
      "first_name": "Имя",        # опционально
      "last_name": "Фамилия"     # опционально
    }
    Логика:
    - создаёт запись в api.User
    - если AUTH_USER_MODEL != api.User, пытается создать запись в модели аутентификации (create_user)
    Возвращает сериализованные данные api.User (без пароля).
    """
    def post(self, request):
        data = request.data or {}
        email = (data.get('email') or '').strip().lower()
        password = data.get('password')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()

        if not email or not password:
            return Response({"error": "email и password обязательны."},
                            status=status.HTTP_400_BAD_REQUEST)

        # validate password with Django validators (if configured)
        try:
            validate_password(password)
        except django_exceptions.ValidationError as ve:
            return Response({"error": "Неподходящий пароль.", "details": ve.messages},
                            status=status.HTTP_400_BAD_REQUEST)

        # Не создавать дубликаты по email
        if User.objects.filter(email=email).exists():
            return Response({"error": "Пользователь с таким email уже существует (api.User)."},
                            status=status.HTTP_400_BAD_REQUEST)

        AuthUser = get_user_model()
        created_auth_user = None
        # Если модель аутентификации — не наша api.User, создаём запись в ней
        try:
            if AuthUser is not User:
                # Используем стандартный create_user если доступен
                create_user_fn = getattr(AuthUser.objects, 'create_user', None)
                if callable(create_user_fn):
                    created_auth_user = create_user_fn(username=email, email=email,
                                                       password=password,
                                                       first_name=first_name, last_name=last_name)
                else:
                    # fallback: создать объект и установить пароль
                    created_auth_user = AuthUser.objects.create(username=email, email=email,
                                                               first_name=first_name, last_name=last_name)
                    if hasattr(created_auth_user, 'set_password'):
                        created_auth_user.set_password(password)
                        created_auth_user.save()
        except IntegrityError:
            return Response({"error": "Пользователь с таким email уже существует (auth)."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # логируем и продолжаем попытаться создать api.User
            # (детали ошибки возвращаем в dev-режиме)
            return Response({"error": "Не удалось создать запись в модели аутентификации.", "detail": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            api_user = User.objects.create(email=email, first_name=first_name, last_name=last_name)
        except IntegrityError:
            # роллбек: удалить созданного auth-пользователя, если он был создан
            if created_auth_user is not None:
                try:
                    created_auth_user.delete()
                except Exception:
                    pass
            return Response({"error": "Пользователь с таким email уже существует (api.User)."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # удаляем auth-пользователя при ошибке
            if created_auth_user is not None:
                try:
                    created_auth_user.delete()
                except Exception:
                    pass
            return Response({"error": "Ошибка при создании api пользователя.", "detail": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = UserSerializer(api_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


try:
    from rest_framework.authtoken.models import Token
    _HAS_TOKEN = True
except Exception:
    Token = None
    _HAS_TOKEN = False

class LoginView(APIView):
    """
    POST: { "email": "...", "password": "..." }
    Если установлен django-rest-framework authtoken — возвращает token.
    Иначе создаёт сессию (login) и возвращает данные пользователя.
    """
    def post(self, request):
        data = request.data or {}
        email = (data.get('email') or '').strip().lower()
        password = data.get('password')

        if not email or not password:
            return Response({"error": "email и password обязательны."}, status=status.HTTP_400_BAD_REQUEST)

        # Попытки аутентификации: username=email и email=email (для кастомных backend-ов)
        user = authenticate(request, username=email, password=password)
        if user is None:
            user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)
        if not getattr(user, "is_active", True):
            return Response({"error": "Пользователь не активен."}, status=status.HTTP_403_FORBIDDEN)

        # Если установлен TokenAuth — возвращаем токен
        if _HAS_TOKEN:
            token, _ = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)

        # Иначе делаем session login (cookie) и возвращаем данные пользователя
        login(request, user)
        serializer = UserSerializer(user)
        return Response({"message": "Logged in", "user": serializer.data}, status=status.HTTP_200_OK)
# ...existing code...

logger = logging.getLogger(__name__)

# Попытка импортировать сериализатор для отображения/валидации профиля
try:
    from api.serializers import UserSerializer  # если у вас сериализатор в другом месте — скорректируйте импорт
    _HAS_SERIALIZER = True
except Exception:
    UserSerializer = None
    _HAS_SERIALIZER = False

# Поддержка Token (если установлен DRF authtoken)
try:
    from rest_framework.authtoken.models import Token
    _HAS_TOKEN = True
except Exception:
    Token = None
    _HAS_TOKEN = False

User = get_user_model()

class ProfileView(APIView):
    """
    GET: возвращает профиль текущего пользователя.
    PUT/PATCH: обновляет профиль (поля: first_name, last_name, profile и т.д.).
    Требует аутентификацию.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if _HAS_SERIALIZER and UserSerializer:
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        # fallback: минимальный ответ
        data = {
            "id": getattr(user, "id", None),
            "email": getattr(user, "email", None),
            "first_name": getattr(user, "first_name", ""),
            "last_name": getattr(user, "last_name", ""),
            "profile": getattr(user, "profile", None),
        }
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request):
        return self._update(request, partial=True)

    def put(self, request):
        return self._update(request, partial=False)

    def _update(self, request, partial=False):
        user = request.user
        payload = request.data or {}

        if _HAS_SERIALIZER and UserSerializer:
            serializer = UserSerializer(instance=user, data=payload, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # fallback: ручное обновление безопасных полей
        allowed = ("first_name", "last_name", "profile")
        changed = False
        for k in allowed:
            if k in payload:
                try:
                    setattr(user, k, payload[k])
                    changed = True
                except Exception:
                    logger.exception("Can't set attribute %s on user", k)
        if changed:
            try:
                user.save()
            except Exception as e:
                logger.exception("Failed to save user")
                return Response({"error": "Failed to save profile", "detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return self.get(request)


class LogoutView(APIView):
    """
    Разлогинивает пользователя:
    - удаляет token (если используется TokenAuth),
    - вызывает django.logout() для session auth.
    Требует аутентификацию.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # удалить токены, если есть
        if _HAS_TOKEN and Token is not None:
            try:
                Token.objects.filter(user=user).delete()
            except Exception:
                logger.exception("Failed to delete token for user %s", getattr(user, "id", None))

        # завершить сессию
        try:
            logout(request)
        except Exception:
            logger.exception("Logout failed for user %s", getattr(user, "id", None))

        return Response({"detail": "Logged out"}, status=status.HTTP_200_OK)