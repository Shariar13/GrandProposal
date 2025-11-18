from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('save-proposal/', views.save_proposal_view, name='save_proposal'),
    path('delete-proposal/<int:proposal_id>/', views.delete_proposal_view, name='delete_proposal'),
    path('download-proposal/<int:proposal_id>/', views.download_proposal_view, name='download_proposal'),
]