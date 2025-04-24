# tours/api/filters.py
import django_filters
from tours.models import Excursion, InterestTag # Убедись, что модели импортированы

class ExcursionFilter(django_filters.FilterSet):
    # Фильтр по тегам (интересам)
    # Мы будем принимать slug тегов в параметре запроса 'tags'
    # Например: /api/v1/excursions/?tags=history,food
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', # Фильтруем по полю 'slug' в связанной модели 'InterestTag'
        to_field_name='slug',   # Поле в InterestTag, по которому ищем совпадения
        queryset=InterestTag.objects.all(), # Откуда берем возможные значения
        label='Теги интересов (по slug через запятую)',
        # conjoined=True, # Раскомментируй, если нужно искать экскурсии, у которых есть ВСЕ перечисленные теги (по умолчанию - хотя бы один)
    )

    # Можно добавить и другие поля для фильтрации, если нужно
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte', label='Мин. цена')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte', label='Макс. цена')
    destination = django_filters.NumberFilter(field_name="destination__id", label='ID Направления') # Фильтр по ID направления

    class Meta:
        model = Excursion
        # Перечисляем поля модели, по которым можно фильтровать напрямую
        # + добавляем наши кастомные фильтры ('tags', 'min_price', 'max_price', 'destination')
        fields = ['excursion_type', 'destination', 'tags', 'min_price', 'max_price']