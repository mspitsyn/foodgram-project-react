from django.db.models import F, Sum

from recipes.models import IngredientAmount


def get_list_ingridients(user):
    shopping_list = IngredientAmount.objects.filter(
        recipe__cart__user=user
    ).values(
        name=F('ingredients__name'),
        measurement_unit=F('ingredients__measurement_unit')
    ).annotate(amount=Sum('amount')).values_list(
        'ingredients__name', 'amount', 'ingredients__measurement_unit'
    )
    shopping_cart = '\n'.join([
        f'{ingredient["ingredients__name"]} - {ingredient["amount"]} '
        f'{ingredient["ingredients__measurement_unit"]}'
        for ingredient in shopping_list
    ])
    return shopping_cart
