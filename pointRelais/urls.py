from django.urls import path
from . import views

urlpatterns = [
    path('',views.Index,name="index"),
    path('login',views.Login,name="pr_login"),
    path('logout',views.Logout,name="pr_logout"),
    path('<id>/update',views.UpdatePR,name="update"),
    path('<id>/detail',views.PrDetail,name="detail"),
    path("search",views.Search,name="search"),
    path('addPr',views.AddPr,name="add-pr")
]