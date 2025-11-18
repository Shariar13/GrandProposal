from django.urls import path
from home import views
from home import views_enhanced

urlpatterns = [
    # Home and Dashboard
    path('', views_enhanced.home, name='home'),
    path('dashboard/', views_enhanced.dashboard, name='dashboard'),

    # Proposal Type Selection
    path('proposal-type/<int:proposal_type_id>/', views_enhanced.proposal_type_detail, name='proposal_type_detail'),

    # Proposal Generation (New Enhanced)
    path('generate/new/', views_enhanced.generate_proposal_new, name='generate_proposal_new'),

    # Proposal Management
    path('proposals/', views_enhanced.my_proposals, name='my_proposals'),
    path('proposal/<int:proposal_id>/', views_enhanced.proposal_detail, name='proposal_detail'),
    path('proposal/<int:proposal_id>/delete/', views_enhanced.delete_proposal, name='delete_proposal'),
    path('proposal/<int:proposal_id>/export/<str:format>/', views_enhanced.export_proposal, name='export_proposal'),
    path('save-proposal/', views_enhanced.save_proposal, name='save_proposal'),

    # Analytics
    path('analytics/', views_enhanced.user_analytics, name='user_analytics'),

    # Legacy endpoints (keep for backward compatibility)
    path('generate/', views.generate_proposal_stream, name='generate_proposal_legacy'),
    path('enhance/', views.enhance_proposal_stream, name='enhance_proposal_legacy'),
]