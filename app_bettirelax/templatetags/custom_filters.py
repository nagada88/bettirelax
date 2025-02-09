from django import template

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
