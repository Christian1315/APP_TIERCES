from django.urls import path
from . import views

urlpatterns = [
    path('<str:identifiant>/pointRelais',views.Login,name="pr_login"),
    path('<id>/<str:identifiant>/update',views.UpdatePR,name="update"),
    path('<id>/<str:identifiant>/detail',views.PrDetail,name="detail"),
    path("<str:identifiant>/search",views.Search,name="search"),
    path('addPr',views.AddPr,name="add-pr")
]