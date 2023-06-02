from django import template

from _modules.getRequest import getData
from _modules.__env import __BASE_URL
_BASE_URL = __BASE_URL

register=template.Library()

@register.simple_tag
def getLivreur(id):
    url = _BASE_URL + "/livreur/%s/detail"%id
    r = getData(url)
    data = r.json()
    return data['nom'] + ' '+ data['prenom']

@register.simple_tag
def getRelayPointName(id):
    url = _BASE_URL + "/relaypoints/%s/getRP"%id
    res = getData(url)
    data = res.json()
    return data['nom']

@register.simple_tag
def getQuartierName(id):
    quartiers = "https://decoupage-bj.innov-prime.com/quartiers/"
    #ICI ON AURA BESOIN D'URL QUI RECUPERE UN QUARTIER EN FONCTION DE SON ID