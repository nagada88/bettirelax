from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def thousand_separator(value):
    try:
        value = int(value)
        return "{:,.0f}".format(value).replace(",", ".")  # Ezres elválasztás ponttal
    except (ValueError, TypeError):
        return value  # Ha nem szám, akkor visszaadja az eredeti értéket
    

@register.filter
def get_item(obj, key):
    """Ha obj dictionary, akkor visszaadja a kulcs értékét, különben üres string"""
    if isinstance(obj, dict):
        return obj.get(key, "")
    return ""

@register.filter
def concat(value, arg):
    """ Összefűzi a két stringet a template-ben. """
    return f"{value}{arg}"


@register.filter
def repeat(value, count):
    """
    Ismétli a megadott értéket a `count` számú alkalommal, különálló <span> elemekben.
    Példa: {{ '★'|repeat:3 }} => <span>★</span><span>★</span><span>★</span>
    """
    try:
        count = int(count)
        # Generálunk annyi <span>-t, ahány csillagot kérünk
        result = ''.join(f'<span>{value}</span>' for _ in range(count))
        return mark_safe(result)  # Biztonságos HTML visszaadás
    except (ValueError, TypeError):
        return ''
