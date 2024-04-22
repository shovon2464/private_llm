from django.urls import path
from .views import IsActiveView,RetriveInfoView,RecievePDFView,RetriveSummaryView,RetriveInfoLatestView,RetriveSummaryLatestView

urlpatterns = [
    path('isactive/', IsActiveView.as_view(), name='is-active'),
    path('retriveinfo/', RetriveInfoView.as_view(), name='retrive-info'),
    path('retrivesummary/', RetriveSummaryView.as_view(), name='retrive-summary'),
    path('retriveinfolatest/', RetriveInfoLatestView.as_view(), name='retrive-summary'),
    path('retrivesummarylatest/', RetriveSummaryLatestView.as_view(), name='retrive-summary'),
    path('recievepdf/', RecievePDFView.as_view(), name='receive-pdf')
]