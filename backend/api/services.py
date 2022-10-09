from django.db.models import F, Sum

from recipes.models import IngredientAmount


def get_list_ingridients(user):
    ingredients = IngredientAmount.objects.filter(
        recipe__cart__user=user
    ).values(
        name=F('ingredients__name'),
        measurement_unit=F('ingredients__measurement_unit')
    ).annotate(amount=Sum('amount')).values_list(
        'ingredients__name', 'amount', 'ingredients__measurement_unit'
    )
    shopping_cart = ''.join(
        f'{key} - {value} - {unit}\n' for key, value, unit in ingredients
    )
    return shopping_cart
