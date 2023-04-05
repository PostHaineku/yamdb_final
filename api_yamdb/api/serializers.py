from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "name",
            "slug",
        )
        lookup_field = "slug"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            "name",
            "slug",
        )
        lookup_field = "slug"


class TitleGetSerializers(serializers.ModelSerializer):
    genre = GenreSerializer(
        many=True,
    )
    category = CategorySerializer()
    rating = serializers.IntegerField(required=False)
    year = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )


class TitlePutPostPatchSerializers(serializers.ModelSerializer):
    """Нельзя добавлять произведения, которые еще не вышли
    (год выпуска не может быть больше текущего).
    При добавлении нового произведения требуется указать
    уже существующие категорию и жанр.
    """

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field="slug",
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field="slug",
    )
    rating = serializers.IntegerField(required=False)
    year = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)

    def validate(self, data):
        request = self.context["request"]
        title_id = self.context["request"].parser_context["kwargs"]["title_id"]
        author = self.context["request"].user
        review = Review.objects.filter(author=author, title=title_id)
        if request.method == "POST":
            if review.exists():
                raise serializers.ValidationError(
                    "Можно оставить только одно ревью"
                )
        return data

    class Meta:
        model = Review
        fields = ("id", "author", "text", "pub_date", "score")
        validators = [UniqueTogetherValidator]


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date")


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.RegexField(r"^[\w.@+-]+")
    email = serializers.EmailField(required=True)

    def validate_username(self, value):
        if value == "me":
            raise serializers.ValidationError(
                "Нельзя создавать пользователя с таким именем"
            )
        return value


class UserObtainTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
