from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя на сайте'
    )
    password = models.CharField(
        max_length=12,
        unique=True,
    )
    email = models.EmailField(
        max_length=50,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    subscriptions = models.ManyToManyField(
        'self',
        verbose_name='Любимые авторы',
        symmetrical=False
    )
    favorites = models.ManyToManyField(
        'recipes.Recipe',
        verbose_name='Избранные рецепты',
        related_name='favorites_of_users'
    )
    cart = models.ManyToManyField(
        'recipes.Recipe',
        verbose_name='Покупки',
        related_name='shopping_cart'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
