from django.urls import path
from home import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate_proposal_stream, name='generate_proposal'),
    path('enhance/', views.enhance_proposal_stream, name='enhance_proposal'),
]