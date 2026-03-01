from django.urls import path
from . import views
from .views import ProductMasterAPI,GenerateBillAPI,PurchaseHistoryListAPI,DenominationAPI

urlpatterns = [
    # path('', billing_page),
    # path('bill/', bill_page),
    path("products/", views.ProductMasterAPI.as_view(),name='products-data'),
    path("generate-bill/", views.GenerateBillAPI.as_view(),name='generate-bills'),
    path("purchase-history/", views.PurchaseHistoryListAPI.as_view(),name='purchase-history'),
    path("denominations/", views.DenominationAPI.as_view(),name='denominations'),

]

