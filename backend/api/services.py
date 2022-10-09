from django.db.models import F, Sum
from django.template.loader import render_to_string
from weasyprint import HTML

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
    shopping_cart = render_to_string('recipes/pdf_template.html',
                                     {'ingredients': shopping_list})
    html = HTML(string=shopping_cart)
    result = html.write_pdf()
    return result
