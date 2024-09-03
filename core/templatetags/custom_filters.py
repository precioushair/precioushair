from django import template

register = template.Library()

@register.filter
def get_quantity(cart, product):
    return cart.get_quantity_of_product(product)

