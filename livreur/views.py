from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.paginator import Paginator

from _modules.getRequest import getData,postData,patchData
from _modules.__env import __BASE_URL,__DELIVERY_STATUS

_BASE_URL = __BASE_URL
DELIVERY_STATUS = __DELIVERY_STATUS

def DELIVERY_MAN_RENDER(request,url=_BASE_URL + "/livreur/getDeliveryMans",paginate=True):
    
    #RECUPERATION DES LIVRAISONS DEPUIS L'API
    r = getData(url)
    delivery_mans = r.json()
    delivery_mans_count = len(delivery_mans)


    if paginate:
        #GESTION DE LA PAGINATION
        paginator_delivery_man= Paginator(delivery_mans,3)
        page_number_delivery_man = request.GET.get('page')
        page_obj_delivery_man = paginator_delivery_man.get_page(page_number_delivery_man)

        context ={
            'delivery_mans_count':delivery_mans_count,
            'page_obj_delivery_man' : page_obj_delivery_man,
        }
        return render(request,"livreur/livreur.html",context)
    else:
        context ={
            'delivery_mans':delivery_mans['delivery_mans'],
            'delivery_mans_count':delivery_mans_count,
        }
        return render(request,"livreur/livreur.html",context)

def HOME_REDIRECTION(request,message):
    messages.error(request,message)
    return redirect('/')


def Index(request):
    #SI LE USER DEMEURE CONNECTE
    if request.user.is_authenticated:
            #AFFICHAGE DE LA PAGE DES LIVREURS
        return DELIVERY_MAN_RENDER(request)
    else:
        return HOME_REDIRECTION(redirect,'Veuillez vous connectez!!')
    
def AddDeliveryMan(request):
    #SI LE USER DEMEURE CONNECTE
    if request.user.is_authenticated:
        if request.method == 'POST':
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            phone = request.POST.get('phone')
            agence = request.POST.get('agence')
            email = request.POST.get('email')
            status = request.POST.get('status')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if not password == confirm_password:
                messages.error(request,"Les mots de passe ne sont pas conforme")
                return DELIVERY_MAN_RENDER(request)

            data = {
                'nom':nom,
                'prenom':prenom,
                'phone':phone,
                'agence':agence,
                'colis_geres':0,
                'colis_a_gerer':0,
                'email':email,
                'status':status,
                'password':password
            }

            url = _BASE_URL + "/livreur/create"
            r = postData(url,data)
            
            if r.status_code == 201:
                messages.success(request,"Livreur ajouté avec succès!!")
                return DELIVERY_MAN_RENDER(request)
            else:
                messages.error(request,"Echec d'ajout de livreur!!")
                return DELIVERY_MAN_RENDER(request)
        else:
            return DELIVERY_MAN_RENDER(request)
    else:
        return HOME_REDIRECTION(redirect,'Veuillez vous connectez!!')

def Search(request):
    if request.user.is_authenticated:
        searching = request.POST.get('searching')
        
        #VALIDATION DE L'INPUT DE RECHERCHE
        if searching =="":
            messages.error(request,"Ce champ est réquis!")
            return redirect('/livreurs')

        
        #RECUPERATION DES LIVRAISONS DEPUIS L'API
        url = _BASE_URL + "/livreur/%s/search"%searching
        r = getData(url)
        data = r.json()

        if data.get('detail'):
            messages.success(request,"Aucune livraison trouvée")
            return redirect('/login')
        else:
            messages.success(request,"Résultats de la recherche")
            return DELIVERY_MAN_RENDER(request,url,paginate=False)
        
    else:
        return HOME_REDIRECTION(request,"Veuillez-vous connectez!!")

def DeliveryManDetail(request,deliveryManId):

    if request.user.is_authenticated:
        #RECUPERATION DU LIVREUR DEPUIS L'API
        url = _BASE_URL + "/livreur/%s/detail"%deliveryManId
        r = getData(url)

        #RECUPERATION DES LIVRAISONS QUI LUI SONT ATTACHEES DEPUIS L'API
        _url = _BASE_URL + "/delivery/deliveryMan/%s/deliveries"%deliveryManId
        _r = getData(_url)
        his_deliveries = _r.json()

        #RECUPERATION DE TOUTES LES LIVRAISONS
        __url = _BASE_URL + "/delivery/deliveries"
        __r = getData(__url)

        alldeliveries = __r.json()

        context ={
            'deliveryman':r.json(),
            'his_deliveries':his_deliveries,
            'alldeliveries':alldeliveries
        }

        return render(request,"livreur/livreur-detail1.html",context)
    else:
        return HOME_REDIRECTION(request,"Veuillez-vous connectez!!")

def UpdateDeliveryMan(request,deliveryManId):
    if request.user.is_authenticated:
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        phone = request.POST.get('phone')
        agence = request.POST.get('agence')
        email = request.POST.get('email')
        status = request.POST.get('status')

        data = {
            'nom':nom,
            'prenom':prenom,
            'phone':phone,
            'agence':agence,
            'status':status,
            'email':email
        }

        url = _BASE_URL + "/livreur/%s/update"%deliveryManId
        r = patchData(url,data)

        if r.status_code == 200:
            messages.success(request,"Livreur modifié avec succès!!")
            return redirect("/livreurs/%s/detail"%deliveryManId)
        else:
            messages.success(request,"Echec de modification du livreur")
            return redirect("/livreurs/%s/detail"%deliveryManId)
    else:
        return HOME_REDIRECTION(request,"Veuillez-vous connectez!!")

def Affect_To_Delivery(request,deliveryManId):

    if request.user.is_authenticated:
        if request.method == 'GET':
            return redirect("/delivery/%s/update_delivery"%deliveryId)
        
        deliveryId = request.POST.get('deliveryId')

        __url = _BASE_URL + "/delivery/%s/update_delivery"%deliveryId
        __data = {
            'deliveryMan':deliveryManId,
        }

        #ENREGISTREMENT DE L'UPDATE DE LA LIVRAISON DANS LA DB
        r = patchData(__url,__data)


        if r.status_code == 200:
            #RECUPERATION DE CE LIVREUR ET L'ACTULISATION DE SON **colis_a_gerer**
            url = _BASE_URL + "/livreur/%s/detail"%deliveryManId
            r = getData(url)
            deliveryMan = r.json()

            colis_a_gerer = deliveryMan['colis_a_gerer']
            data = {
                'colis_a_gerer':colis_a_gerer+1 #INCREMENTATION DES COLIS A GERER POUR CE LIVREUR
            }

            _url = _BASE_URL + "/livreur/%s/update"%deliveryManId
            res = patchData(_url,data)#ACTUALISATION DANS LA DB

            messages.success(request,"Livreur affecté(e) avec succès!!")
            return redirect("/livreurs/%s/detail"%deliveryManId)
        else:
            messages.success(request,"Affectation répétée ou échouée!!")
            return redirect("/livreurs/%s/detail"%deliveryManId)
    else:
        return HOME_REDIRECTION(request,"Veuillez-vous connectez!!")
  