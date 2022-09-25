from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингридиента',
        max_length=200,
    )
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_for_ingredient'
            )]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=7,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipe_images/',
        blank=True,
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        related_name='recipes',
        verbose_name='Тэги',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(
            1, message='Минимальное время приготовления 1 минута')],
        verbose_name='Время приготовления, минут',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_user_recipe',
            ),
        )

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_cart_user',
            ),)

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class IngredientAmount(models.Model):
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Продукты рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='В каких рецептах',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиентов',
        validators=[MinValueValidator(
            1, message='Минимальное количество ингридиентов 1'
            )],
    )

    class Meta:
        verbose_name = 'Количество ингридиентов'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredients'],
                                    name='unique_ingredients_recipe')
        ]

    def __str__(self):
        return f'{self.ingredients} - {self.amount}'
