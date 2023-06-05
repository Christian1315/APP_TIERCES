from _modules.getRequest import getData,postData,patchData
from _modules.__env import __BASE_URL

_BASE_URL = __BASE_URL

def PR_COLIS_MANAGEMENT(delivery_termined,relay_point_id):
    if delivery_termined:#QUAND LE STATUS DE LA LIVRAISON PASSE A IS_TERMINE
        #GESTION DE LA STATUT **colis_geres** DU POINT RELAIS
        getRP_url = _BASE_URL + "/relaypoints/%s/getRP"%relay_point_id
        getRP = getData(getRP_url).json()
        rp_old_colis_geres = getRP.get('colis_geres')

        update_rp_data = {
            "colis_geres":rp_old_colis_geres + 1
        }

        update_rp_url = _BASE_URL + "/relaypoints/%s/update"%relay_point_id
        patchData(update_rp_url,update_rp_data)

    else:
        #GESTION DE LA STATUT **colis_geres** DU POINT RELAIS
        getRP_url = _BASE_URL + "/relaypoints/%s/getRP"%relay_point_id
        getRP = getData(getRP_url).json()
        rp_old_colis_geres = getRP.get('colis_geres')

        update_rp_data = {
            "colis_geres":rp_old_colis_geres - 1#DECREMENTATION DE LA VARIBLE **colis_geres** DU POINT RELAIS
        }
        
        update_rp_url = _BASE_URL + "/relaypoints/%s/update"%relay_point_id
        patchData(update_rp_url,update_rp_data)
