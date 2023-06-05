from django.urls import path
from . import views

urlpatterns = [
    # ====== USING GENERICS ====== #
    path("", views.Index,name="home"),
    path("login", views._Login,name="login"),
    path("logout", views.Logout,name="logout"),
    path("deliveryMan/deliveries", views.Deliveries,name="deliveries"),
    path("livraison-show/<id>", views.LivraisonDetail,name="livraison-show"),
    path("change_delivery_statut/<deliveryId>", views.ChangeDeliveryStatut,name="ChangeDeliveryStatut"),
    path("search",views.Search,name="search")
]
