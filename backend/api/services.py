from django.db.models import F, Sum

from recipes.models import IngredientAmount


def get_list_ingridients(user):
    ingredients = IngredientAmount.objects.filter(
            recipes__shoppingcart__user=user
    ).values(
        name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit')
    ).annotate(amount=Sum('amount')).values_list(
        'ingredient__name', 'amount', 'ingredient__measurement_unit'
    )
    shopping_cart = ''.join(
        f'{key} - {value} - {unit}\n' for key, value, unit in ingredients
    )
    return shopping_cart
