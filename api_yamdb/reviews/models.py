from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название категории")
    slug = models.SlugField(
        unique=True, verbose_name="slug названия категории"
    )


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название жанра")
    slug = models.SlugField(unique=True, verbose_name="slug Названия жанра")


class Title(models.Model):
    name = models.TextField("Название")
    year = models.SmallIntegerField("Год выпуска", validators=[validate_year])
    description = models.TextField("Описание", blank=True, null=True)
    genre = models.ManyToManyField(
        Genre,
        related_name="genre_titles",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="category_titles",
        null=True,
    )


class Review(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author_reviews",
        verbose_name="Автор ревью",
    )

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name="title_reviews",
        verbose_name="Название произведения",
    )

    text = models.TextField(verbose_name="Текст ревью")
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True,
    )

    score = models.SmallIntegerField(
        validators=(
            MinValueValidator(
                1, message="Оценка не может быть меньше единицы"
            ),
            MaxValueValidator(
                10, message="Оценка не может быть больше десяти"
            ),
        ),
        verbose_name="Оценка",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_review"
            ),
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="review_comments",
        verbose_name="Ревью",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author_comments",
        verbose_name="Автор комментария",
    )

    text = models.TextField(verbose_name="Текст комментария")
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True, db_index=True
    )
