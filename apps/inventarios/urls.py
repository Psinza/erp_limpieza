from django.urls import path
from . import views

app_name = 'inventarios'

urlpatterns = [
    path('stock/', views.InventarioGlobalListView.as_view(), name='stock_list'),
    path('', views.InventarioGlobalListView.as_view(), name='dashboard'), # same for now
]
