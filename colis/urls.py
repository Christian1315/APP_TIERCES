from django.urls import path
from . import views

urlpatterns = [
    # ====== USING GENERICS ====== #
    path("", views.Index,name="home"),
    path("login", views._Login,name="login"),
    path("deliveryMan/<int:delivery_man_id>/deliveries", views.Deliveries,name="deliveries"),
    path("livraison-show/<id>/<delivery_man_id>", views.LivraisonDetail,name="livraison-show"),
    path("change_delivery_statut/<deliveryId>/<delivery_man_id>", views.ChangeDeliveryStatut,name="ChangeDeliveryStatut"),
    path("search",views.Search,name="search")
]
