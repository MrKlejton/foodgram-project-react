from distutils.util import strtobool

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Sum
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    EasyRecipeSerializer, IngredientSerializer, RecipeSerializer,
    TagSerializer, UserCreateSerializer, UserSerializer,
    UserSerializerWithRecipes
)
from api.utils import create_shopping_cart
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_object(self):
        if self.action == 'me':
            return self.request.user
        return super().get_object()
    
    def get_queryset(self):
        if self.action == 'subscriptions':
            return self.request.user.subscriptions.all()
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action in ('subscriptions', 'subscribe'):
            return UserSerializerWithRecipes
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action == 'create':
            return (AllowAny(),)
        if self.action in ('me', 'set_password', 'subscriptions', 'subscribe'):
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(('get',), detail=False)
    def me(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @action(('post',), detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(('get',), detail=False)
    def subscriptions(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(('post', 'delete'), detail=False,
            url_path=r'(?P<pk>\d+)/subscribe')
    def subscribe(self, request, *args, **kwargs):
        user_object = self.get_object()
        user = self.request.user

        if user_object == user:
            return Response(
                {'errors': 'Вы не можете подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if self.request.method == 'POST':
            if user_object in user.subscriptions.all():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.subscriptions.add(user_object)
            return Response(
                self.get_serializer(user_object).data,
                status=status.HTTP_201_CREATED
            )
        if not (user_object in user.subscriptions.all()):
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.subscriptions.remove(user_object)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = CustomPagination
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            is_favorited = self.request.query_params.get('is_favorited')
            is_in_shopping_cart = self.request.query_params.get(
                'is_in_shopping_cart'
            )
            try:
                if is_favorited is not None and strtobool(is_favorited):
                    return self.request.user.favorites.all()

                if (is_in_shopping_cart is not None
                   and strtobool(is_in_shopping_cart)):
                    return self.request.user.cart.all()
            except ValueError:
                pass

        return super().get_queryset()

    def get_serializer_class(self):
        if self.action in ('favorite', 'shopping_cart'):
            return EasyRecipeSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            tags=self.request.data['tags']
        )

    def perform_update(self, serializer):
        serializer.save(
            tags=self.request.data['tags'],
            ingredients=self.request.data['ingredients']
        )

    @action(
        ('post', 'delete'),
        detail=False,
        url_path=r'(?P<pk>\d+)/favorite'
    )
    def favorite(self, request, *args, **kwargs):
        recipe = self.get_object()
        user = self.request.user

        if self.request.method == 'POST':
            if recipe in user.favorites.all():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.favorites.add(recipe)
            return Response(
                self.get_serializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        if not (recipe in user.favorites.all()):
            return Response(
                {'errors': 'Рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.favorites.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ('post', 'delete'),
        detail=False,
        url_path=r'(?P<pk>\d+)/shopping_cart'
    )
    def shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        recipe = self.get_object()

        if self.request.method == 'POST':
            if recipe in user.cart.all():
                return Response(
                    {'errors': 'Рецепт в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.cart.add(recipe)
            return Response(
                self.get_serializer(recipe).data,
                status=status.HTTP_201_CREATED
            )

        if not (recipe in user.cart.all()):
            return Response(
                {'errors': 'Рецепта нет в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ('get',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients_cart = (
            AmountIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).order_by(
                'ingredient__name'
            ).annotate(ingredient_value=Sum('amount'))
        )
        return create_shopping_cart(ingredients_cart)
