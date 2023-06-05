from myUser.models import MyUser
from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.contrib import messages
from _modules.getRequest import getData,postData,patchData

from django.contrib.auth import login,logout


from django.contrib.auth.models import User

from _modules.__env import __BASE_URL,__DELIVERY_STATUS

_BASE_URL = __BASE_URL
DELIVERY_STATUS = __DELIVERY_STATUS

def PR_RENDER(request,url,paginate=True):
    #RECUPERATION DES PR DEPUIS L'API
    r = getData(url)
    pr = r.json()
    pr_count = len(pr)

    #S'IL A UN IDENTIFIANT VALIDE
    if paginate:
        #GESTION DE LA PAGINATION
        paginator_pr= Paginator(pr,3)
        page_number_pr = request.GET.get('page')
        page_obj_pr = paginator_pr.get_page(page_number_pr)

        context ={
            'pr_count':pr_count,
            'page_obj_pr' : page_obj_pr,
        }
        return render(request,"pointRelais/pr.html",context)
    else:
        context ={
            'pr_count':pr_count,
            'pr':pr,
        }
        return render(request,"pointRelais/pr.html",context)
      
def HOME_REDIRECTION(request,message):
    messages.error(request,message)
    return redirect("/pointRelais")

def Index(request):
    if request.user.is_authenticated:
        _url = _BASE_URL + "/relaypoints/getAll"
        return PR_RENDER(request,_url)
    return render(request,"pointRelais/index.html")

def Login(request):
    if request.method == 'POST':
        identifiant = request.POST.get('identifiant')

        if not identifiant:
            messages.error(request,'Le champ est réquis!')
            return redirect('/pointRelais')
        
        url = _BASE_URL + "/relaypoints/%s/search"%identifiant
        r = getData(url)
        data = r.json() 

        if data.get('detail'):
            messages.error(request,"Echec!! Vérifiez vos données puis essayez à nouveau")
            return redirect("/pointRelais")
        else:#CE POINT RELAIS EXISTE DANS L'API FEDRELAY
            user = MyUser.objects.get(username=identifiant)
            login(request, user)#ON LE CONNECTE DANS L'APP TIERCES
            messages.success(request,"Vous êtes connecté(e) avec succès!!")
            #RECUPERATION DE TOUT LES POINTS RELAIS & AFFICHAGE DE LA LISTE 
            _url = _BASE_URL + "/relaypoints/getAll"
            return PR_RENDER(request,_url)
    else:
        return redirect('/pointRelais')

def Logout(request):
    logout(request)#DECONNEXION DU PR DAN SLES APPs TIERCES
    return HOME_REDIRECTION(request,"Vous êtes déconecté(e)")
  
def Search(request):
    if request.user.is_authenticated:#S'IL EST AUTHENTIFIE
        if request.user.is_superuser or request.user.is_RelayPoint:#S'IL EST UN PR OU UN ADMIN
            if request.method == 'POST':
                searching = request.POST.get('searching')
                
                #VALIDATION DE L'INPUT DE RECHERCHE
                if searching =="":
                    messages.error(request,"Ce champ est réquis!")
                    url = _BASE_URL + "/relaypoints/getAll"
                    return PR_RENDER(request,url)
                
                
                #RECUPERATION DES POINTS RELAIS DEPUIS RECHERCHES L'API
                url = _BASE_URL + "/relaypoints/%s/search"%searching
                r = getData(url)
                data = r.json()

                if data.get('detail'):
                    messages.success(request,"Aucun point relais trouvé")
                    url = _BASE_URL + "/relaypoints/getAll"
                    return PR_RENDER(request,url)
                else:
                    messages.success(request,"Résultats de la recherche")
                    return PR_RENDER(request,url,paginate=False)
            else:
                url = _BASE_URL + "/relaypoints/getAll"
                return PR_RENDER(request,url)
    
    return HOME_REDIRECTION(request,"Veuillez-vous authentifiez!!")


def PrDetail(request,id):
    if request.user.is_authenticated:#S'IL EST AUTHENTIFIE
        if request.user.is_superuser or request.user.is_RelayPoint:#S'IL EST UN PR OU UN ADMIN
            #RECUPERATION DU POINT RELAIS DEPUIS L'API
            url = _BASE_URL + "/relaypoints/%s/getRP"%id
            r = getData(url)
            ce_pointRelai = r.json()

            #RECUPERATION DE TOUTES LES LIVRAISONS ASSOCIEES A CE POINT RELAIS DEPUIS L'API
            _url = _BASE_URL + "/delivery/pointRelais/%s/deliveries"%id
            _r = getData(_url)
            RP_DELIVERIES = _r.json()

            context ={
                'ce_pointRelai':ce_pointRelai,
                'RP_DELIVERIES':RP_DELIVERIES,
            }
            return render(request,'pointRelais/pr-detail.html',context)

    return HOME_REDIRECTION(request,"Veuillez-vous authentifiez!!")


def AddPr(request):
    if request.user.is_authenticated:#S'IL EST AUTHENTIFIE
        if request.user.is_superuser or request.user.is_RelayPoint:#S'IL EST AUTHENTIFIE COMME UN PR OU UN ADMIN
            if request.method == 'GET':
                if request.user.is_superuser:#'IL EST UN ADMIN
                    #RECUPERATION DE TOUT LES DEPARTEMENTS
                    dep_url = "https://decoupage-bj.innov-prime.com/departements/"
                    DEPARTEMENTS = getData(dep_url).json()  

                    #RECUPERATION DE TOUTES LES COMMUNES
                    com_url = "https://decoupage-bj.innov-prime.com/communes/"
                    COMMUNES = getData(com_url).json()  

                    #RECUPERATION DE TOUT LES QUARTIERS
                    quart_url = "https://decoupage-bj.innov-prime.com/quartiers/"
                    QUARTIERS = getData(quart_url).json()  

                    #RECUPERATION DE TOUT LES ARRONDISSEMENTS
                    arrond_url = "https://decoupage-bj.innov-prime.com/arrondissements/"
                    ARRONDISSEMENTS = getData(arrond_url).json() 

                    context ={
                        'DEPARTEMENTS':DEPARTEMENTS,
                        'COMMUNES':COMMUNES,
                        'QUARTIERS':QUARTIERS,
                        'ARRONDISSEMENTS':ARRONDISSEMENTS
                    }
                    return render(request,'pointRelais/add-pr.html',context)
                else:
                    return HOME_REDIRECTION(request,"Veuillez-vous connectez!!")
            else:
                nom = request.POST.get('nom')
                pays = request.POST.get('pays')
                departement = request.POST.get('departement')
                commune = request.POST.get('commune')
                arrondissement = request.POST.get('arrondissement')
                quartier = request.POST.get('quartier')
                localisation = request.POST.get('localisation')
                identifiant = request.POST.get('identifiant')
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                status = request.POST.get('status')
                map_adresse = request.POST.get('map_adresse')


                if not password == confirm_password:
                    messages.error(request,"Les mots de passe ne sont pas conformes!!")
                    return redirect("/pointRelais/addPr")
            
                data = {
                    'quartier_id':quartier,
                    'nom':nom,
                    'pays':pays,
                    'departement':departement,
                    'commune':commune,
                    'arrondissement':arrondissement,
                    'localisation':localisation,
                    'identifiant':identifiant,
                    'password':password,
                    'status':status,
                    'map_address':map_adresse,
                    "colis_geres": 0,
                    "colis_a_gerer": 0
                }

                #ENREGISTREMENT DANS LA DB
                url = _BASE_URL + "/relaypoints/create"
                r = postData(url,data)


                if r.status_code == 200 or r.status_code == 201:
                    #ENREGISTREMENT DU PR COMME UN USER DANS LES APPs TIERCES
                    relay_point = MyUser.objects.create_user(
                        username=identifiant,
                        password=password
                    )

                    relay_point.is_RelayPoint = True
                    relay_point.save()
                    #
                    messages.success(request,'Point de relais ajouté avec succès!!')
                    return redirect('/pointRelais/addPr')
                else:
                    if r.json().get('identifiant'):#SI L'IDENTIFIANT EXISTE DEJA DANS LA DB DE L'API
                        messages.success(request,'Cet identifiant existe déjà! \n Veuillez tapez un autre!')
                        return redirect('/pointRelais/addPr')
                    
                    messages.success(request,'Une erreur est survenue!!     Veuillez réessayez à nouveau!')
                    return redirect('/pointRelais/addPr')
            
    return HOME_REDIRECTION(request,"Veuillez-vous connectez!!")      
        


def UpdatePR(request,id):
    if request.user.is_authenticated:#S'IL EST AUTHENTIFIE
        if request.user.is_superuser or request.user.is_RelayPoint:#S'IL EST AUTHENTIFIE COMME UN PR OU UN ADMIN
            nom = request.POST.get('nom')
            pays = request.POST.get('pays')
            departement = request.POST.get('departement')
            commune = request.POST.get('commune')
            arrondissement = request.POST.get('arrondissement')
            localisation = request.POST.get('localisation')
            status = request.POST.get('status')

            data = {
                'nom':nom,
                'pays':pays,
                'departement':departement,
                'commune':commune,
                'arrondissement':arrondissement,
                'localisation':localisation,
                'status':status,
            }

            url = _BASE_URL + "/relaypoints/%s/update"%id
            r = patchData(url,data)

            if r.status_code == 200  or r.status_code==201:
                messages.success(request,"Point relais modifié avec succès!!")
                return redirect(f"/pointRelais/{id}/detail")
            else:
                messages.success(request,"Echec de modification du point relais")
                return redirect(f"/pointRelais/{id}/detail")

    return HOME_REDIRECTION(request,"Veuillez-vous connectez!!") 