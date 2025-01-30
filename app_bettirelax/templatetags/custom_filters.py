from django import template

register = template.Library()

@register.filter
def thousand_separator(value):
    try:
        value = int(value)
        return "{:,.0f}".format(value).replace(",", ".")  # Ezres elválasztás ponttal
    except (ValueError, TypeError):
        return value  # Ha nem szám, akkor visszaadja az eredeti értéket