from djoser.serializers import UserCreateSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredientsSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('measurement_unit', 'name')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 0.'
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj in user.subscriptions.all()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AmountIngredientsSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=False
    )
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        if user.is_authenticated:
            return recipe in user.favorites.all()
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        if user.is_authenticated:
            return recipe in user.cart.all()
        return False

    def validate_tags(self, tags_ids):
        if not all(isinstance(tag, int) for tag in tags_ids):
            raise ValidationError(
                {'tags': 'Проверьте список тегов.'}
            )
        tags = Tag.objects.filter(pk__in=tags_ids)
        if not tags:
            raise ValidationError(
                {'tags': 'Тэги отсутствуют или не существуют.'}
            )
        return tags

    def validation(self, data):
        data['tags'] = self.validate_tags(data['tags'])

        return super().run_validation(data)

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Минимальное время приготовления 1 минута.'
            )
        return value

    def validate(self, attrs):
        ingredients = attrs['recipe_ingredients']
        if not ingredients:
            raise serializers.ValidationError(
                'Ингредиенты отсутствуют.'
            )

        ingredients_already_checked = set()

        for ing in ingredients:
            ingredient = ing['ingredient']['id']
            if ingredient in ingredients_already_checked:
                raise serializers.ValidationError(
                    f'Вы добавили {ingredient.name} повторно.'
                )
            ingredients_already_checked.add(ingredient)

        return super().validate(attrs)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_with_amount = validated_data.pop(
            'recipe_ingredients'
        )

        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.add(*tags)

        for ingredient in ingredients_with_amount:
            recipe.add_ingredient_amount(
                ingredient['ingredient']['id'],
                ingredient['amount']
            )

        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients_with_amount = validated_data.pop(
            'recipe_ingredients'
        )

        super().update(recipe, validated_data)

        recipe.tags.clear()
        recipe.tags.add(*tags)

        recipe.ingredients.clear()
        for ingredient in ingredients_with_amount:
            recipe.add_ingredient_amount(
                ingredient['ingredient']['id'],
                ingredient['amount']
            )

        return recipe


class EasyRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')
        read_only_fields = ('id', 'name', 'cooking_time', 'image')


class UserCreateSerializer(DjoserUserSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }


class UserSerializerWithRecipes(UserSerializer):
    recipes = EasyRecipeSerializer(
        many=True
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()
