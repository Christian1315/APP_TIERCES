from django.urls import path
from . import views

urlpatterns = [
    # ====== USING GENERICS ====== #
    path("", views.Index,name="home"),
    path("addDeliveryMan", views.AddDeliveryMan,name="addDeliveryMan"),
    path("search",views.Search,name="search"),
    path("<deliveryManId>/detail",views.DeliveryManDetail,name="detail"),
    path("<deliveryManId>/update",views.UpdateDeliveryMan,name="update"),
    path("affect_to_delivery/<deliveryManId>",views.Affect_To_Delivery,name="affect_to_delivery")
]
