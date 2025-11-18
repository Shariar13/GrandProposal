"""
Enhanced Views for Grant Proposal Generation
Integrates new RAG system and OpenAI generation
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import time
from datetime import datetime

from authentication.models import (
    ProposalType, ProposalTemplate, SavedProposal,
    ProposalAnalytics, UserProfile
)
from .enhanced_rag_system import EnhancedRAGSystem
from .enhanced_proposal_generator import EnhancedProposalGenerator


# Global instances for caching
_rag_system = None
_proposal_generator = None


def get_rag_system():
    """Get or create RAG system instance"""
    global _rag_system
    if _rag_system is None:
        _rag_system = EnhancedRAGSystem()
    return _rag_system


def get_proposal_generator():
    """Get or create proposal generator instance"""
    global _proposal_generator
    if _proposal_generator is None:
        api_key = settings.OPENAI_API_KEY
        _proposal_generator = EnhancedProposalGenerator(api_key=api_key)
    return _proposal_generator


@login_required
def dashboard(request):
    """Main dashboard with proposal type selection"""
    # Get all active proposal types
    proposal_types = ProposalType.objects.filter(is_active=True).order_by('name')

    # Get user's recent proposals
    recent_proposals = SavedProposal.objects.filter(
        user=request.user,
        is_latest=True
    ).order_by('-created_at')[:5]

    # Get user statistics
    user_profile = request.user.profile
    total_proposals = SavedProposal.objects.filter(user=request.user).count()
    total_words = sum(
        p.word_count for p in SavedProposal.objects.filter(user=request.user)
    )

    context = {
        'proposal_types': proposal_types,
        'recent_proposals': recent_proposals,
        'total_proposals': total_proposals,
        'total_words': total_words,
        'user_profile': user_profile,
    }

    return render(request, 'dashboard.html', context)


@login_required
def proposal_type_detail(request, proposal_type_id):
    """Show details of a specific proposal type and start generation"""
    proposal_type = get_object_or_404(ProposalType, id=proposal_type_id, is_active=True)

    # Get templates for this proposal type
    templates = proposal_type.templates.all().order_by('section_order')

    context = {
        'proposal_type': proposal_type,
        'templates': templates,
    }

    return render(request, 'proposal_type_detail.html', context)


@login_required
@require_http_methods(["POST"])
def generate_proposal_new(request):
    """
    New generation endpoint that:
    1. Runs RAG to collect comprehensive research data
    2. Uses OpenAI to generate complete proposal
    """
    # Get form data
    proposal_type_id = request.POST.get('proposal_type_id')
    title = request.POST.get('title', '').strip()
    keywords = request.POST.get('keywords', '').strip()
    description = request.POST.get('description', '').strip()

    # Validation
    if not all([proposal_type_id, title, description]):
        return JsonResponse({
            'error': 'Missing required fields: proposal_type_id, title, and description are required'
        }, status=400)

    try:
        proposal_type = ProposalType.objects.get(id=proposal_type_id, is_active=True)
    except ProposalType.DoesNotExist:
        return JsonResponse({'error': 'Invalid proposal type'}, status=400)

    # Start time for analytics
    start_time = time.time()

    def event_stream():
        """Stream generation progress to client"""
        try:
            # Step 1: RAG Data Collection
            yield format_sse({
                'type': 'phase',
                'phase': 'rag',
                'message': '🔍 Collecting research data from academic databases...'
            })

            # Build search query
            search_query = f"{title} {keywords} {description}"

            # Run RAG system
            rag_system = get_rag_system()
            rag_data = rag_system.comprehensive_search(
                query=search_query,
                max_results_per_source=50
            )

            yield format_sse({
                'type': 'rag_complete',
                'total_papers': rag_data['total_papers'],
                'message': f'✓ Collected {rag_data["total_papers"]} research papers with citations'
            })

            # Step 2: AI Generation
            yield format_sse({
                'type': 'phase',
                'phase': 'generation',
                'message': '🤖 Generating proposal using AI with research data...'
            })

            # Generate proposal
            generator = get_proposal_generator()
            for update in generator.generate_complete_proposal(
                proposal_type=proposal_type,
                title=title,
                keywords=keywords,
                description=description,
                rag_data=rag_data
            ):
                yield format_sse(update)

            # Step 3: Save to database
            # This will be handled by frontend

            # Track analytics
            execution_time = time.time() - start_time
            ProposalAnalytics.objects.create(
                user=request.user,
                action='generate',
                metadata={
                    'proposal_type': proposal_type.name,
                    'papers_retrieved': rag_data['total_papers'],
                    'title': title
                },
                execution_time=execution_time
            )

            # Update user profile stats
            profile = request.user.profile
            profile.total_proposals_generated += 1
            profile.save()

            yield format_sse({
                'type': 'complete',
                'message': '✓ Proposal generation complete!',
                'execution_time': execution_time
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            yield format_sse({
                'type': 'error',
                'message': f'Error: {str(e)}'
            })

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@login_required
@require_http_methods(["POST"])
def save_proposal(request):
    """Save generated proposal to database"""
    try:
        data = json.loads(request.body)

        proposal_type_id = data.get('proposal_type_id')
        title = data.get('title')
        keywords = data.get('keywords', '')
        description = data.get('description')
        content = data.get('content')
        content_json = data.get('content_json', {})
        rag_data = data.get('rag_data', {})

        # Validation
        if not all([proposal_type_id, title, description, content]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # Get proposal type
        proposal_type = get_object_or_404(ProposalType, id=proposal_type_id)

        # Create proposal
        proposal = SavedProposal.objects.create(
            user=request.user,
            proposal_type=proposal_type,
            title=title,
            keywords=keywords,
            description=description,
            content=content,
            content_json=content_json,
            retrieved_papers=rag_data.get('papers', []),
            citations_data=rag_data.get('citation_library', {}),
            status='draft'
        )

        # Update profile stats
        profile = request.user.profile
        profile.total_proposals_saved += 1
        profile.total_words_generated += proposal.word_count
        profile.save()

        # Track analytics
        ProposalAnalytics.objects.create(
            user=request.user,
            proposal=proposal,
            action='save',
            metadata={'title': title}
        )

        return JsonResponse({
            'success': True,
            'proposal_id': proposal.id,
            'message': 'Proposal saved successfully'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def proposal_detail(request, proposal_id):
    """View a saved proposal"""
    proposal = get_object_or_404(
        SavedProposal,
        id=proposal_id,
        user=request.user
    )

    # Track view analytics
    ProposalAnalytics.objects.create(
        user=request.user,
        proposal=proposal,
        action='view'
    )

    context = {
        'proposal': proposal,
    }

    return render(request, 'proposal_detail.html', context)


@login_required
def my_proposals(request):
    """List all user's proposals"""
    proposals = SavedProposal.objects.filter(
        user=request.user,
        is_latest=True
    ).select_related('proposal_type').order_by('-created_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        proposals = proposals.filter(status=status_filter)

    # Filter by proposal type
    type_filter = request.GET.get('type')
    if type_filter:
        proposals = proposals.filter(proposal_type__code=type_filter)

    context = {
        'proposals': proposals,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'proposal_types': ProposalType.objects.filter(is_active=True),
    }

    return render(request, 'my_proposals.html', context)


@login_required
@require_http_methods(["POST"])
def delete_proposal(request, proposal_id):
    """Delete a proposal"""
    proposal = get_object_or_404(SavedProposal, id=proposal_id, user=request.user)

    # Track analytics
    ProposalAnalytics.objects.create(
        user=request.user,
        action='delete',
        metadata={'title': proposal.title}
    )

    proposal.delete()

    return JsonResponse({'success': True, 'message': 'Proposal deleted successfully'})


@login_required
def export_proposal(request, proposal_id, format='docx'):
    """Export proposal in various formats"""
    proposal = get_object_or_404(SavedProposal, id=proposal_id, user=request.user)

    # Track analytics
    ProposalAnalytics.objects.create(
        user=request.user,
        proposal=proposal,
        action='download',
        metadata={'format': format}
    )

    if format == 'txt':
        response = HttpResponse(proposal.content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{proposal.title}.txt"'
        return response

    elif format == 'json':
        data = {
            'title': proposal.title,
            'keywords': proposal.keywords,
            'description': proposal.description,
            'content': proposal.content,
            'sections': proposal.content_json,
            'metadata': {
                'word_count': proposal.word_count,
                'page_count': proposal.page_count,
                'citation_count': proposal.citation_count,
                'created_at': proposal.created_at.isoformat(),
            }
        }
        response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{proposal.title}.json"'
        return response

    # Default to plaintext for now
    # TODO: Implement DOCX and PDF export
    response = HttpResponse(proposal.content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{proposal.title}.txt"'
    return response


def format_sse(data: dict) -> str:
    """Format data as Server-Sent Event"""
    return f"data: {json.dumps(data)}\n\n"


@login_required
def user_analytics(request):
    """Show user analytics and statistics"""
    profile = request.user.profile

    # Get proposals statistics
    proposals = SavedProposal.objects.filter(user=request.user)
    total_proposals = proposals.count()
    total_words = sum(p.word_count for p in proposals)
    total_citations = sum(p.citation_count for p in proposals)

    # Proposals by type
    proposals_by_type = {}
    for prop_type in ProposalType.objects.all():
        count = proposals.filter(proposal_type=prop_type).count()
        if count > 0:
            proposals_by_type[prop_type.name] = count

    # Recent activity
    recent_analytics = ProposalAnalytics.objects.filter(
        user=request.user
    ).select_related('proposal').order_by('-created_at')[:20]

    context = {
        'profile': profile,
        'total_proposals': total_proposals,
        'total_words': total_words,
        'total_citations': total_citations,
        'proposals_by_type': proposals_by_type,
        'recent_analytics': recent_analytics,
    }

    return render(request, 'user_analytics.html', context)


# Keep old views for backward compatibility
def home(request):
    """Redirect to dashboard if authenticated, otherwise show landing page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')
