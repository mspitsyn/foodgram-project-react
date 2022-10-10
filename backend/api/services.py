from django.db.models import F, Sum

from recipes.models import IngredientAmount


def get_list_ingridients(user):
    ingredients = IngredientAmount.objects.filter(
        recipe__cart__user=user
    ).values(
        name=F('ingredients__name'),
        measurement_unit=F('ingredients__measurement_unit')
    ).annotate(amount=Sum('amount')).order_by
    shopping_cart = ''.join(
        f'{ing.get("name")} - {ing.get("amount")}'
        f'{ing.get("measurement_unit")}\n' for ing in ingredients
    )
    return shopping_cart
