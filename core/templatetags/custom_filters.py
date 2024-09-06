from django import template

register = template.Library()

@register.filter
def get_quantity(cart, product):
    return cart.get_quantity_of_product(product)

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})
