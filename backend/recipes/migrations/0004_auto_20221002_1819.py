# Generated by Django 2.2.19 on 2022-10-02 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20221002_1749'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientamount',
            options={'default_related_name': 'ingridients_recipe', 'verbose_name': 'Количество ингридиента в рецепте', 'verbose_name_plural': 'Количество ингридиентов в рецепте'},
        ),
        migrations.AlterField(
            model_name='ingredientamount',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to='recipes.Ingredient', verbose_name='Ингредиенты рецепта'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, upload_to='recipes/images', verbose_name='Картинка'),
        ),
    ]