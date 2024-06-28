from django.urls import path
from .views import IsActiveView,RetriveInfoView,RecievePDFView,RetriveSummaryView,RetriveInfoLatestView,RetriveSummaryLatestView,ClassifyNaturesView
from .views import CommandGPTView,MakeSpeechToTextView,RedactTextView,RiskAnalysisView

urlpatterns = [
    path('isactive/', IsActiveView.as_view(), name='is-active'),
    path('retriveinfo/', RetriveInfoView.as_view(), name='retrive-info'),
    path('retrivesummary/', RetriveSummaryView.as_view(), name='retrive-summary'),
    path('retriveinfolatest/', RetriveInfoLatestView.as_view(), name='retrive-info-llama3'),
    path('retrivesummarylatest/', RetriveSummaryLatestView.as_view(), name='retrive-summary-llama3'),
    path('classifynatures/', ClassifyNaturesView.as_view(), name='classify-natures-llama3'),
    path('commandgpt/', CommandGPTView.as_view(), name='command-gpt'),
    path('speechtotext/', MakeSpeechToTextView.as_view(), name='speech-to-text'),
    path('redacttext/', RedactTextView.as_view(), name='redact-text'),
    path('riskanalysis/', RiskAnalysisView.as_view(), name='risk-analysis'),
    path('recievepdf/', RecievePDFView.as_view(), name='receive-pdf')
]