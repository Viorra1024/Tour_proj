# tours/templatetags/query_helpers.py
from django import template
from django.http import QueryDict

register = template.Library()

@register.filter(name='discard')
def discard(querydict, keys_to_remove_str):
    """
    Удаляет указанные ключи из QueryDict (копии).
    Принимает строку ключей через запятую.
    Возвращает измененную QueryDict.
    """
    if not isinstance(querydict, QueryDict):
        # Если это не QueryDict, просто возвращаем как есть
        # или можно вернуть пустой QueryDict: return QueryDict()
        return querydict

    keys_to_remove = keys_to_remove_str.split(',')
    mutable_querydict = querydict.copy()
    for key in keys_to_remove:
        key = key.strip() # Убираем пробелы на всякий случай
        if key in mutable_querydict:
            del mutable_querydict[key]
    return mutable_querydict

# Добавим еще один фильтр для удобства, сразу кодирующий результат
@register.filter(name='discard_encode')
def discard_encode(querydict, keys_to_remove_str):
    """
    Удаляет ключи и возвращает urlencode() строки.
    Добавляет '&' в начало, если результат не пустой.
    """
    mutable_querydict = discard(querydict, keys_to_remove_str)
    if mutable_querydict:
        encoded = mutable_querydict.urlencode()
        if encoded:
            return '&' + encoded # Добавляем амперсанд для удобства конкатенации
    return ''