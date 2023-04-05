from datetime import date

from django.core.exceptions import ValidationError


def validate_year(value):
    if 0 < value >= date.today().year:
        raise ValidationError(
            "Некорректный год выпуска",
        )
