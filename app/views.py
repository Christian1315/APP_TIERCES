from django.core.paginator import Paginator
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.shortcuts import render,redirect

from _modules.getRequest import getData,postData,patchData
from _modules.__env import __BASE_URL,__DELIVERY_STATUS,__DELIVERY_STATUS_PR

from _modules.changeStatus import PR_COLIS_MANAGEMENT

_BASE_URL = __BASE_URL
DELIVERY_STATUS = __DELIVERY_STATUS
DELIVERY_STATUS_PR = __DELIVERY_STATUS_PR


def DELIVERY_RENDER(request,url,paginate=True):
    
    #RECUPERATION DES LIVRAISONS DEPUIS L'API
    r = getData(url)
    livraisons = r.json()
    livraisons_count = len(livraisons)

    if paginate:
        #GESTION DE LA PAGINATION
        paginator_livraison= Paginator(livraisons,3)
        page_number_livraison = request.GET.get('page')
        page_obj_livraison = paginator_livraison.get_page(page_number_livraison)

        context ={
            'livraisons_count':livraisons_count,
            'page_obj_livraison' : page_obj_livraison,
        }
        return render(request,"livraison.html",context)
    else:
        context ={
            'livraisons_count':livraisons_count,
            'livraison':livraisons,
        }
        return render(request,"livraison.html",context)

def HOME_REDIRECTION(request,message):
    messages.error(request,message)
    return redirect('/')

def Index(request):
    return render(request,"index.html")

def _Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            #CONNEXION DU USER
            login(request,user)

            #ACCES AUX LIVRAISONS
            return redirect('/deliveries')
        else:
            #RETOUR AU HOME PAGE
            return HOME_REDIRECTION(request,"Echec!! Vérifiez vos données puis essayez à nouveau")
    else:
        #SI LE USER DEMEURE CONNECTE
        if request.user.is_authenticated:
            return redirect('/deliveries')
        else:
            #RETOUR AU HOME PAGE
            return HOME_REDIRECTION(request,"Veuillez vous connectez!!")

def Deliveries(request):
    #SI LE USER DEMEURE CONNECTE
    if request.user.is_authenticated:
        #RECUPERATION DE TOUTES LES LIVRAISONS
        url = _BASE_URL + "/delivery/deliveries"
        return DELIVERY_RENDER(request,url)
    #REDIECTION VERS LE HOME PAGE
    return HOME_REDIRECTION(request,"Veuillez-vous connectez!!") 

def _Logout(request):
    logout(request) 
    return HOME_REDIRECTION(request,"Vous êtes déconnecté(e)!")

def LivraisonDetail(request,id):
    
    #RECUPERATION DE TOUT LES LIVREURS
    url = _BASE_URL + "/livreur/getDeliveryMans"
    DELIVERY_MANS = getData(url).json()    

    #RECUPERATION DES LIVRAISONS DEPUIS L'API
    url = _BASE_URL + "/delivery/%s/deliverie"%id
    r = getData(url)
    context ={
        'livraison':r.json(),
        'deliveryMans':DELIVERY_MANS,
        'deliveryStatus':DELIVERY_STATUS,
        'deliveryStatus_pr':DELIVERY_STATUS_PR,#POUR LES POINTS RELAIS
    }
    return render(request,"livraison-voir.html",context)

def Search(request):
    if request.user.is_authenticated:
        searching = request.POST.get('searching')
        
        #VALIDATION DE L'INPUT DE RECHERCHE
        if searching =="":
            messages.error(request,"Ce champ est réquis!")
            return redirect('/deliveries')
        
        #RECUPERATION DES LIVRAISONS DEPUIS L'API
        url = _BASE_URL + "/delivery/%s/search"%searching
        r = getData(url)
        data = r.json()

        if data.get('detail'):
            messages.success(request,"Aucune livraison trouvée")
            return redirect('/login')
        else:
            messages.success(request,"Résultats de la recherche")
            return DELIVERY_RENDER(request,url,paginate=False)
        
    else:
        return HOME_REDIRECTION(request,"Veuillez-vous connectez!!")

def Affect_To_DeliveryMan(request,deliveryId):
    if request.user.is_authenticated:#S'IL EST AUTHENTIFIE
        if request.user.is_superuser or request.user.is_RelayPoint:#S'IL EST AUTHENTIFIE COMME UN PR OU UN ADMIN

            if request.method == 'GET':
                return redirect("/delivery/%s/update_delivery"%deliveryId)

        deliveryManId = request.POST.get("deliverymanId")
        url = _BASE_URL + "/delivery/%s/update_delivery"%deliveryId
        data = {
            'deliveryMan':deliveryManId
        }

        #ENREGISTREMENT DE L'UPDATE DE LA LIVRAISON DANS LA DB
        r = patchData(url,data)

        if r.status_code == 200 or r.status_code == 201:
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

            messages.success(request,"Livraison affectée avec succès!!")
        
            return redirect(f"/livraison-show/{deliveryId}")
        else:
            messages.success(request,"Affectation échoué!!")
            if not request.user.is_authenticated:#S'IL N'EST PAS UN ADMIN(SOIT UN LIVREUR OU UN PR)
                return redirect(f"/livraison-show/{deliveryId}")

            return redirect("/livraison-show/%s"%deliveryId)
    else:
        return HOME_REDIRECTION(request,"Veuillez-vous connectez!!")

def ChangeDeliveryStatut(request,deliveryId):
    if request.user.is_authenticated:#S'IL EST AUTHENTIFIE
        delivery_status = request.POST.get("delivery_status")

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

        #VERIFIONS SI CE STATUS EXISTE DEJA POUR CE COLIS
        colis_url = _BASE_URL + "/delivery/%s/deliverie"%deliveryId
        colis = getData(colis_url).json()

        if colis.get('%s'%delivery_status):#SI CE STATUS EXISTE DEJA
            messages.error(request,"Ce colis est déjà à ce statut!")
            return redirect("/livraison-show/%s"%deliveryId) 

        #ENREGISTREMENT DE L'UPDATE DANS LA DB
        url = _BASE_URL + "/delivery/%s/update_delivery"%deliveryId
        r = patchData(url,data)
        delivery = r.json()

        if r.status_code == 200 or r.status_code == 201:#STATUT CHANGE AVEC SUCCES!
            #GESTION DE LA STATUT **colis_geres** DU LIVREUR
            delivery_received = delivery.get('is_reception')
            deliveryMan = delivery.get('deliveryMan')

            delivery_termined = delivery.get('is_termine')
            relay_point_id = delivery.get('pointRelais')

            #GESTION DE LA STATUT **colis_geres** DU PR
            PR_COLIS_MANAGEMENT(delivery_termined,relay_point_id)
            
            # if deliveryMan: #SI UN LIVREUR LUI EST ASSOCIE
            #     if delivery_received:#SI LE COLIS A ETE RECU
            #         #PASSONS A L'ACTUALLISATION DE **colis_geres** DU LIVREUR DANS LA DB
            #         __url = _BASE_URL + "/livreur/%s/detail"%deliveryMan
            #         r = getData(__url)
            #         delivery_man = r.json()

            #         colis_geres = delivery_man['colis_geres']
            #         data = {
            #             'colis_geres':colis_geres+1 #INCREMENTATION DES COLIS A GERER POUR CE LIVREUR
            #         }
                    
            #         _url = _BASE_URL + "/livreur/%s/update"%deliveryMan
            #         res = patchData(_url,data)#ACTUALISATION DANS LA DB
            
            messages.success(request,"Statut changé avec succès!!")
            return redirect("/livraison-show/%s"%deliveryId)

    if request.user.is_RelayPoint:#S'IL EST UN PR
        messages.error(request,"Veuillez-vous connectez!!")
        return redirect('/pointRelais')
    
    return HOME_REDIRECTION(request,"Veuillez-vous connectez!!")

def AddDelivery(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            #RECUPERATION DE TOUT LES LIVREURS
            url = _BASE_URL + "/livreur/getDeliveryMans"
            DELIVERY_MANS = getData(url).json()    

            #RECUPERATION DE TOUT LES LIVREURS
            _url = _BASE_URL + "/relaypoints/getAll"
            RELAYS_POINTS = getData(_url).json()    

            context ={
                'deliveryMans':DELIVERY_MANS,
                'deliveryStatus':DELIVERY_STATUS,
                'RELAYS_POINTS':RELAYS_POINTS,
            }
            return render(request,"add-livraison.html",context)
        else:
            return HOME_REDIRECTION(request,"Veuillez-vous connectez!!")
        
    else:
        nomEmetteur = request.POST.get('nomEmetteur')
        prenomEmetteur = request.POST.get('prenomEmetteur')
        telephoneEmetteur = request.POST.get('telephoneEmetteur')
        lieuColis = request.POST.get('lieuColis')
        typeColis = request.POST.get('typeColis')
        contenuColis = request.POST.get('description')

        nomDestinataire = request.POST.get('nomDestinataire')
        prenomDestinataire = request.POST.get('prenomDestinataire')
        telephoneDestinataire = request.POST.get('telephoneDestinataire')
        emailDestinataire = request.POST.get('emailDestinataire')

        pointRelais = request.POST.get('pointRelais')

        #GESTION LE L'AFFECTATION D4UNE LIVRAISON A UN LIVREUR
        deliveryMan = request.POST.get('deliverymanId')

        #GESTION DU STATUS DE LA LIVRAISON
        delivery_status = request.POST.get('delivery_status')

        is_lancement=False
        is_enlevement=False
        is_acheminement=False
        is_reception=False
        is_termine=False

        if delivery_status == "is_lancement":
            is_lancement = True
        elif delivery_status == "is_enlevement":
            is_enlevement= True
        elif delivery_status == "is_acheminement":
            is_acheminement = True
        elif delivery_status == "is_reception":
            is_reception = True
        elif delivery_status == "is_termine":
            is_termine = True
        else:
            is_lancement = True

        data = {
            'user':0, #PAR CONVENTION LES USERS DES APPs TIERCES SERONT 0
            'nomEmetteur':nomEmetteur,
            'prenomEmetteur':prenomEmetteur,
            'telephoneEmetteur':telephoneEmetteur,
            'lieuColis':lieuColis,
            'typeColis':typeColis,
            'contenuColis':contenuColis,
            'nomDestinataire':nomDestinataire,
            'prenomDestinataire':prenomDestinataire,
            'telephoneDestinataire':telephoneDestinataire,
            'emailDestinataire':emailDestinataire,
            'pointRelais':pointRelais,
            'deliveryMan':deliveryMan,
            'pointRelais':pointRelais,
            
            "is_lancement":is_lancement,
            "is_enlevement":is_enlevement,
            "is_acheminement":is_acheminement,
            "is_reception":is_reception,
            "is_termine":is_termine
        }

        url = __BASE_URL + "/delivery/create_from_app"
        r = postData(url,data)#LIVRAISON ENREGISTREE DANS LA DB

        if r.status_code == 200:
            this_delivery = r.json()
            ##==========#INCREMENTATION DES COLIS A GERER POUR CE LIVREUR=========###
            deliveryManId = this_delivery.get('deliveryMan') #RECUPERATION DE CE LIVREUR

            if deliveryManId:#SI LE LIVREUR EXISTE DANS LE FORMULAIRE ENVOYE
                #RECUPERATION DU LIVREUR ASSOCIE
                url = _BASE_URL + "/livreur/%s/detail"%deliveryManId
                _r = getData(url)
                deliveryMan = _r.json()#LIVREUR RECUPERE(e)

                colis_a_gerer = deliveryMan['colis_a_gerer']
                data = {
                    'colis_a_gerer':colis_a_gerer+1 #INCREMENTATION DES COLIS A GERER POUR CE LIVREUR
                }
                
                #ACTUALISATION DU LIVREUR DANS LA DB
                _url = _BASE_URL + "/livreur/%s/update"%deliveryManId
                res = patchData(_url,data)#ACTUALISATION DANS LA DB
            
            messages.success(request,'Livraison ajoutée avec succès!!')
            return redirect('/deliveries')
        else:
            messages.success(request,'Echec d\'ajout de livraison!!')
            return redirect('/deliveries')