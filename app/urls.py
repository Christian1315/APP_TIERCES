from django.urls import path
from . import views

urlpatterns = [
    # ====== USING GENERICS ====== #
    path("", views.Index,name="home"),
    path("login", views._Login,name="login"),
    path("deliveries", views.Deliveries,name="deliveries"),
    path("logout", views._Logout,name="logout"),
    path("livraison-show/<id>", views.LivraisonDetail,name="livraison-show"),
    path("livraison/<id>/<str:identifiant>/detail", views.LivraisonDetailForNoAdmin,name="livraison-detail"),
    path("afect_to_deliveryMan/<deliveryId>", views.Affect_To_DeliveryMan,name="afect_to_deliveryMan"),
    path("change_delivery_statut/<int:deliveryId>", views.ChangeDeliveryStatut,name="ChangeDeliveryStatut"),
    path("search",views.Search,name="search"),
    path('addDelivery',views.AddDelivery,name="add-livraison")
]
