from django import template

register = template.Library()


@register.filter
def meu_filtro(value):
    # Lógica do filtro aqui
    return value
