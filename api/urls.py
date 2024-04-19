from django.urls import path
from .views import IsActiveView,RetriveInfoView,RecievePDFView

urlpatterns = [
    path('isactive/', IsActiveView.as_view(), name='is-active'),
    path('retriveinfo/', RetriveInfoView.as_view(), name='retrive-info'),
    path('recievepdf/', RecievePDFView.as_view(), name='receive-pdf')
]