from django import template

register=template.Library()

@register.simple_tag
def attente_colis(a_gerer,geres):
    return int(a_gerer) - int(geres)