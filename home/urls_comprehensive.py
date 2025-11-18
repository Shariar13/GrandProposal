"""
Comprehensive URL Configuration
Routes for all new features
"""
from django.urls import path
from . import views_comprehensive

urlpatterns = [
    # Home and Dashboard
    path('', views_comprehensive.home, name='home'),
    path('dashboard/', views_comprehensive.dashboard, name='dashboard'),

    # Proposal Generation
    path('proposal-type/<int:proposal_type_id>/', views_comprehensive.proposal_type_detail, name='proposal_type_detail'),
    path('generate/comprehensive/', views_comprehensive.generate_proposal_comprehensive, name='generate_proposal_comprehensive'),

    # Dynamic Discovery
    path('discover/calls/', views_comprehensive.discover_funding_calls, name='discover_funding_calls'),
    path('discover/structure/', views_comprehensive.create_dynamic_proposal_structure, name='create_dynamic_proposal_structure'),

    # Proposal Management
    path('proposals/', views_comprehensive.my_proposals, name='my_proposals'),
    path('proposal/<int:proposal_id>/', views_comprehensive.proposal_detail, name='proposal_detail'),

    # Editing Features
    path('section/edit-ai/', views_comprehensive.edit_section_with_ai, name='edit_section_with_ai'),
    path('section/update/', views_comprehensive.update_section_content, name='update_section_content'),

    # Export
    path('proposal/<int:proposal_id>/export/<str:format>/', views_comprehensive.export_proposal, name='export_proposal'),

    # Analytics
    path('analytics/', views_comprehensive.user_analytics, name='user_analytics'),
]
