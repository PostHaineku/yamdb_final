from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.utils import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrStaffOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleGetSerializers, TitlePutPostPatchSerializers,
                          UserObtainTokenSerializer,
                          UserRegistrationSerializer, UserSerializer)
from reviews.models import Category, Genre, Review, Title
from users.models import User


class CategoryViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
):
    """Получить список всех категорий.
    Права доступа: Доступно без токена.
    Создать категорию. Права доступа: Администратор.
    Удалить категорию. Права доступа: Администратор.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("name",)
    search_fields = ("name",)
    ordering_fields = ("name",)
    pagination_class = LimitOffsetPagination
    lookup_field = "slug"


class GenreViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
):
    """Получить список всех жанров.
    Права доступа: Доступно без токена.
    Добавить жанр. Права доступа: Администратор.
    Удалить жанр. Права доступа: Администратор.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("name",)
    search_fields = ("name",)
    ordering_fields = ("name",)
    pagination_class = LimitOffsetPagination
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    """Получить список всех объектов. Права доступа: Доступно без токена.
    Добавить новое произведение. Права доступа: Администратор.
    Информация о произведении. Права доступа: Доступно без токена
    Обновить информацию о произведении. Права доступа: Администратор.
    Удалить произведение. Права доступа: Администратор.
    """

    queryset = Title.objects.all()
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_queryset(self):
        return Title.objects.all().annotate(rating=Avg("title_reviews__score"))

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TitleGetSerializers
        else:
            return TitlePutPostPatchSerializers


class ReviewViewSet(viewsets.ModelViewSet):
    """Получить список всех отзывов или отзыв по id.
    Права доступа: Доступно без токена.
    Добавить новый отзыв. Пользователь может оставить
    только один отзыв на произведение.
    Права доступа: Аутентифицированные пользователи.
    Частично обновить или удалить отзыв по id.
    Права доступа: Автор отзыва, модератор или администратор.
    """

    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title.title_reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Получить список всех комментариев к отзыву по id.
    Получить комментарий для отзыва по id.
    Права доступа: Доступно без токена.
    Добавить новый комментарий для отзыва.
    Права доступа: Аутентифицированные пользователи.
    Частично обновить или удалить комментарий к отзыву по id.
    Права доступа: Автор комментария, модератор или администратор.
    """

    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get("review_id"))
        return review.review_comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, pk=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)


class UserRegistrationView(APIView):
    """Получить код подтверждения на переданный email.
    Права доступа: Доступно без токена."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, create = User.objects.get_or_create(
                **serializer.validated_data
            )
        except IntegrityError:
            raise ValidationError("Неверное имя пользователя или email")
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject="YaMDb регистрация",
            message=f"Ваш код подтверждения: {confirmation_code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTokenObtainView(APIView):
    """Получение JWT-токена в обмен на username и confirmation code.
    Права доступа: Доступно без токена."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserObtainTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        confirmation_code = serializer.validated_data["confirmation_code"]
        user = get_object_or_404(User, username=username)
        if default_token_generator.check_token(user, confirmation_code):
            refresh = RefreshToken.for_user(user)
            return Response(
                {"token": str(refresh.access_token)}, status.HTTP_200_OK
            )
        else:
            return Response(
                "Код активации не верный!", status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    """Получить, изменить, удалить пользователя по username.
    Права доступа: Администратор.
    Получить, изменить, удалить данные своей учетной записи
    Права доступа: Любой авторизованный пользователь."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "username"
    ordering = ["username"]

    @action(
        methods=["get", "patch"],
        detail=False,
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def getbyusername(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        if "role" in serializer.validated_data:
            if serializer.validated_data["role"] != request.user.role:
                return Response(serializer.data, status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
