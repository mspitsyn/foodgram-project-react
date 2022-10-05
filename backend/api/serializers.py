from django.contrib.auth import get_user_model
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import (
    Ingredient, IngredientAmount, Recipe, Tag
)
from users.models import Follow
from .mixins import IngredientMixin

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'id', 'password', 'username',
                  'first_name', 'last_name')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj.id).exists()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    ingredient = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'ingredient', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class RecipeReadSerializer(IngredientMixin, serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time',)


class RecipeWriteSerializer(IngredientMixin, serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    image = Base64ImageField(use_url=True, max_length=None)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def validate(self, data):
        ingredients = data.get('ingredients', None)
        ingredients_set = set()
        for ingredient in ingredients:
            if type(ingredient.get('amount')) is str:
                if not ingredient.get('amount').isdigit():
                    raise serializers.ValidationError(
                        ('Количество ингредиента должно быть числом')
                    )
            if int(ingredient.get('amount')) <= 0:
                raise serializers.ValidationError(
                    ('Минимальное количество ингридиентов 0,1')
                )
            if int(data['cooking_time']) <= 0:
                raise serializers.ValidationError(
                    'Время готовки должно быть больше нуля'
                )
            ingredient_id = ingredient.get('id')
            if ingredient_id in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиент не должен повторяться.'
                )
            ingredients_set.add(ingredient_id)
        data['ingredients'] = ingredients
        return data

    def __add_tags_ingredients(self, instance, **validated_data):
        ingredients = validated_data['ingredients']
        tags = validated_data['tags']
        for tag in tags:
            instance.tags.add(tag)

        IngredientAmount.objects.bulk_create([IngredientAmount(
            recipe=instance,
            ingredients_id=ingredient.get('id'),
            amount=ingredient.get('amount'),
            ) for ingredient in ingredients
        ])
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user
        )
        return self.__add_tags_ingredients(
            recipe, ingredients=ingredients, tags=tags)

    def update(self, instance, validated_data):
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = self.initial_data.get('tags')
        instance = self.__add_tags_ingredients(
            instance, ingredients=ingredients, tags=tags)
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        user = self.context['request'].user
        follow = data['following']
        if user == follow:
            raise serializers.ValidationError(
                'Нельзя подписаться на себя'
            )
        if Follow.objects.filter(
            user=user,
            following=follow
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора'
            )
        return data