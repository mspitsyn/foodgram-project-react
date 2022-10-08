from django.db.models import F


class IngredientMixin:
    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
