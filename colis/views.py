from django.http import HttpResponse, HttpResponseNotFound,Http404,HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.shortcuts import render,redirect

from _modules.getRequest import getData,postData,patchData

from _modules.__env import __BASE_URL,__DELIVERY_STATUS

_BASE_URL = __BASE_URL
DELIVERY_STATUS = __DELIVERY_STATUS

def COLIS_RENDER(request,url,delivery_man_id,paginate=True):
    
    #RECUPERATION DES LIVRAISONS DEPUIS L'API
    r = getData(url)
    colis = r.json()
    colis_count = len(colis)

    if paginate:
        #GESTION DE LA PAGINATION
        paginator_livraison= Paginator(colis,3)
        page_number_livraison = request.GET.get('page')
        page_obj_livraison = paginator_livraison.get_page(page_number_livraison)

        context ={
            'livraisons_count':colis_count,
            'page_obj_livraison' : page_obj_livraison,
            'delivery_man_id':delivery_man_id,
        }
        return render(request,"colis/livraison.html",context)
    else:
        context ={
            'livraisons_count':colis_count,
            'livraison':colis,
            'delivery_man_id':delivery_man_id,
        }
        return render(request,"colis/livraison.html",context)

def HOME_REDIRECTION(request,delivery_man_id,message):
    messages.error(request,message)
    return redirect("/colis/deliveryMan/%s/deliveries"%delivery_man_id)

def Index(request):
    return render(request,"colis/index.html")

def _Login(request):
    if request.method == 'POST':
        password = request.POST['password']
        url = _BASE_URL + "/livreur/%s/getByPass"%password
        r = getData(url)
        data = r.json() 

        delivery_man_id = data.get('id')

        if data.get('detail'):
            messages.error(request,"Echec!! Vérifiez vos données puis essayez à nouveau")
            return redirect("/colis")
        else:
            return redirect('/colis/deliveryMan/%s/deliveries'%delivery_man_id)
    else:
        return HOME_REDIRECTION(request,delivery_man_id,"Veuillez vous connecter!")

def Deliveries(request,delivery_man_id):
    if not delivery_man_id:
        return HOME_REDIRECTION(request,delivery_man_id,"Veuillez vous connecter!!")
    
    url = _BASE_URL + "/delivery/deliveryMan/%s/deliveries"%delivery_man_id
    return COLIS_RENDER(request,url,delivery_man_id)

def LivraisonDetail(request,id,delivery_man_id):
    
    if not delivery_man_id:
        return HOME_REDIRECTION(request,delivery_man_id,"Veuillez vous connecter!!")

    #RECUPERATION DES LIVRAISONS DEPUIS L'API
    url = _BASE_URL + "/delivery/%s/deliverie"%id
    r = getData(url)
    context ={
        'livraison':r.json(),
        'deliveryStatus':DELIVERY_STATUS,
        'delivery_man_id':delivery_man_id
    }
    return render(request,"colis/livraison-voir.html",context)

def Search(request):
    delivery_man_id = request.POST.get('delivery_man_id')

    if not delivery_man_id:
        return HOME_REDIRECTION(request,"Veuillez vous connectez!!")

    searching = request.POST.get('searching')
    #VALIDATION DE L'INPUT DE RECHERCHE
    if searching =="":
        messages.error(request,"Ce champ est réquis!")
        return redirect("/colis/deliveryMan/%s/deliveries"%delivery_man_id)
    
    #RECUPERATION DES LIVRAISONS DEPUIS L'API
    url = _BASE_URL + "/delivery/%s/search"%searching
    r = getData(url)
    data = r.json()

    if data.get('detail'):
        messages.success(request,"Aucun résultat trouvé")
        return redirect("/colis/deliveryMan/%s/deliveries"%delivery_man_id)
    else:
        messages.success(request,"Résultats de la recherche")
        return COLIS_RENDER(request,url,delivery_man_id,paginate=False)

def ChangeDeliveryStatut(request,deliveryId,delivery_man_id):

    if not delivery_man_id:
        return HOME_REDIRECTION(request,delivery_man_id,"Veuillez vous connecter!!")

    delivery_status = request.POST.get("delivery_status")
    url = _BASE_URL + "/delivery/%s/update_delivery"%deliveryId
    
    #INITIALISATION DU DATA
    data = {
        "is_lancement":False,
        "is_enlevement":False,
        "is_acheminement":False,
        "is_reception":False,
        "is_termine":False
    }
    #UPDATE DU DATA AVANT ENREGISTREMENT DANS LA DB
    if delivery_status == "is_lancement":
        data['is_lancement'] = True
    elif delivery_status == "is_enlevement":
        data['is_enlevement'] = True
    elif delivery_status == "is_acheminement":
        data['is_acheminement'] = True
    elif delivery_status == "is_reception":
        data['is_reception'] = True
    elif delivery_status == "is_termine":
        data['is_termine'] = True

    #ENREGISTREMENT DE L'UPDATE DANS LA DB
    patchData(url,data)

    #RECUPERATION DE LA LIVRAISON DEPUIS L'API
    _url = _BASE_URL + "/delivery/%s/deliverie"%deliveryId
    _r = getData(_url)
    delivery = _r.json()


    delivery_received = delivery['is_reception']
    deliveryMan = delivery['deliveryMan']

    if deliveryMan: #SI UN LIVREUR LUI EST ASSOCIE
        if delivery_received:#SI LE COLIS A ETE RECU
            # if delivery_status == "is_reception":#Si le colis est déjà étiquité comme reçu dans la DB
            #     messages.success(request,"Statut changé avec succès!!")
            #     return redirect("/colis/livraison-show/%s"%deliveryId)
            
            #Si non,
            #PASSONS A L'ACTUALLISATION DE **colis_geres** DU LIVREUR DANS LA DB
            __url = _BASE_URL + "/livreur/%s/detail"%deliveryMan
            r = getData(__url)
            delivery_man = r.json()

            colis_geres = delivery_man['colis_geres']
            data = {
                'colis_geres':colis_geres+1 #INCREMENTATION DES COLIS A GERER POUR CE LIVREUR
            }
            
            _url = _BASE_URL + "/livreur/%s/update"%deliveryMan
            res = patchData(_url,data)#ACTUALISATION DANS LA DB
            
    messages.success(request,"Statut changé avec succès!!")
    return redirect(f"/colis/livraison-show/{deliveryId}/{delivery_man_id}")