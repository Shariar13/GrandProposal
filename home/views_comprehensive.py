"""
Comprehensive Views System
Integrates all features: RAG+Web, Dynamic Discovery, Export, Visuals
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import time
from datetime import datetime
from io import BytesIO

from authentication.models import (
    ProposalType, ProposalTemplate, SavedProposal,
    ProposalAnalytics, UserProfile, ProposalSection
)
from .enhanced_rag_with_web import EnhancedRAGWithWeb
from .enhanced_proposal_generator import EnhancedProposalGenerator
from .web_scraper import WebScraperSystem
from .dynamic_proposal_discovery import DynamicProposalDiscovery
from .export_engine import ProposalExportEngine
from .professional_visuals_generator import ProfessionalVisualsGenerator


# Global instances
_rag_system = None
_proposal_generator = None
_web_scraper = None
_discovery_system = None
_export_engine = None
_visuals_generator = None


def get_rag_system():
    global _rag_system
    if _rag_system is None:
        _rag_system = EnhancedRAGWithWeb()
    return _rag_system


def get_proposal_generator():
    global _proposal_generator
    if _proposal_generator is None:
        api_key = settings.OPENAI_API_KEY
        _proposal_generator = EnhancedProposalGenerator(api_key=api_key)
    return _proposal_generator


def get_web_scraper():
    global _web_scraper
    if _web_scraper is None:
        _web_scraper = WebScraperSystem()
    return _web_scraper


def get_discovery_system():
    global _discovery_system
    if _discovery_system is None:
        _discovery_system = DynamicProposalDiscovery()
    return _discovery_system


def get_export_engine():
    global _export_engine
    if _export_engine is None:
        _export_engine = ProposalExportEngine()
    return _export_engine


def get_visuals_generator():
    global _visuals_generator
    if _visuals_generator is None:
        _visuals_generator = ProfessionalVisualsGenerator()
    return _visuals_generator


@login_required
def home(request):
    """Home page - redirect to dashboard if authenticated"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


@login_required
def dashboard(request):
    """Main dashboard"""
    proposal_types = ProposalType.objects.filter(is_active=True).order_by('name')
    recent_proposals = SavedProposal.objects.filter(
        user=request.user,
        is_latest=True
    ).order_by('-created_at')[:5]

    user_profile = request.user.profile
    total_proposals = SavedProposal.objects.filter(user=request.user).count()
    total_words = sum(p.word_count for p in SavedProposal.objects.filter(user=request.user))

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
    """Show proposal type details and generation form"""
    proposal_type = get_object_or_404(ProposalType, id=proposal_type_id, is_active=True)
    templates = proposal_type.templates.all().order_by('section_order')

    context = {
        'proposal_type': proposal_type,
        'templates': templates,
    }

    return render(request, 'proposal_type_detail.html', context)


@login_required
def discover_funding_calls(request):
    """Discover open funding calls dynamically"""
    funding_body = request.GET.get('funding_body', '')
    research_area = request.GET.get('research_area', '')

    discovery = get_discovery_system()

    # Discover open calls
    calls = discovery.discover_open_calls(funding_body, research_area)

    return JsonResponse({
        'success': True,
        'calls': calls,
        'count': len(calls)
    })


@login_required
def create_dynamic_proposal_structure(request):
    """Create proposal structure dynamically from web searches"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    funding_body = request.POST.get('funding_body')
    research_area = request.POST.get('research_area')

    if not funding_body:
        return JsonResponse({'error': 'Funding body required'}, status=400)

    discovery = get_discovery_system()

    # Create dynamic structure
    structure = discovery.create_dynamic_proposal_structure(
        funding_body, research_area or ""
    )

    return JsonResponse({
        'success': True,
        'structure': structure
    })


@login_required
@require_http_methods(["POST"])
def generate_proposal_comprehensive(request):
    """
    Comprehensive proposal generation with:
    - Web scraping + API search
    - Dynamic templates
    - Professional visuals
    - Auto-export
    """
    # Get form data
    proposal_type_id = request.POST.get('proposal_type_id')
    title = request.POST.get('title', '').strip()
    keywords = request.POST.get('keywords', '').strip()
    description = request.POST.get('description', '').strip()
    custom_urls = request.POST.get('custom_urls', '').strip()
    include_news = request.POST.get('include_news', 'true') == 'true'

    # Parse custom URLs
    url_list = [url.strip() for url in custom_urls.split('\n') if url.strip()] if custom_urls else None

    # Validation
    if not all([title, description]):
        return JsonResponse({'error': 'Title and description required'}, status=400)

    try:
        if proposal_type_id:
            proposal_type = ProposalType.objects.get(id=proposal_type_id, is_active=True)
        else:
            # Create dynamic proposal type
            proposal_type = None
    except ProposalType.DoesNotExist:
        return JsonResponse({'error': 'Invalid proposal type'}, status=400)

    start_time = time.time()

    def event_stream():
        try:
            # Step 1: Comprehensive RAG (APIs + Web Scraping)
            yield format_sse({
                'type': 'phase',
                'phase': 'rag',
                'message': '🌐 Searching academic databases + web sources...'
            })

            search_query = f"{title} {keywords} {description}"
            rag_system = get_rag_system()

            rag_data = rag_system.comprehensive_search_with_web(
                query=search_query,
                max_results_per_source=50,
                include_news=include_news,
                custom_urls=url_list
            )

            yield format_sse({
                'type': 'rag_complete',
                'total_papers': rag_data['total_papers'],
                'total_news': rag_data.get('total_news', 0),
                'sources': rag_data.get('sources', {}),
                'message': f'✓ Found {rag_data["total_papers"]} papers + {rag_data.get("total_news", 0)} news articles'
            })

            # Step 2: Generate Professional Visuals
            yield format_sse({
                'type': 'phase',
                'phase': 'visuals',
                'message': '📊 Generating professional tables and graphs...'
            })

            visuals_gen = get_visuals_generator()
            visuals = visuals_gen.generate_all_visuals(
                rag_data,
                proposal_type.name if proposal_type else "Research Proposal"
            )

            yield format_sse({
                'type': 'visuals_complete',
                'total_visuals': visuals['total_count'],
                'message': f'✓ Generated {visuals["total_count"]} professional figures and tables'
            })

            # Step 3: AI Generation
            yield format_sse({
                'type': 'phase',
                'phase': 'generation',
                'message': '🤖 Generating proposal with AI...'
            })

            generator = get_proposal_generator()

            # Collect all sections
            all_sections = []
            full_text_parts = []

            for update in generator.generate_complete_proposal(
                proposal_type=proposal_type,
                title=title,
                keywords=keywords,
                description=description,
                rag_data=rag_data
            ):
                if update['type'] == 'section_complete':
                    all_sections.append({
                        'name': update['section_name'],
                        'content': update['content'],
                        'word_count': update.get('word_count', 0)
                    })
                    full_text_parts.append(f"## {update['section_name']}\n\n{update['content']}\n\n")

                yield format_sse(update)

            # Compile full proposal text
            full_proposal_text = '\n'.join(full_text_parts)

            # Step 4: Save to database
            yield format_sse({
                'type': 'phase',
                'phase': 'saving',
                'message': '💾 Saving proposal...'
            })

            saved_proposal = SavedProposal.objects.create(
                user=request.user,
                proposal_type=proposal_type,
                title=title,
                description=description,
                content=full_proposal_text,
                content_json={'sections': all_sections},
                retrieved_papers=rag_data.get('papers', []),
                citations_data=rag_data.get('bibliography', {}),
                word_count=sum(s['word_count'] for s in all_sections),
                citation_count=len(rag_data.get('bibliography', {}).get('apa', [])),
                status='draft',
                version=1,
                is_latest=True
            )

            # Save individual sections
            for idx, section in enumerate(all_sections, 1):
                ProposalSection.objects.create(
                    proposal=saved_proposal,
                    section_name=section['name'],
                    section_order=idx,
                    content=section['content'],
                    word_count=section['word_count']
                )

            # Update user profile
            profile = request.user.profile
            profile.total_proposals_generated += 1
            profile.total_proposals_saved += 1
            profile.total_words_generated += saved_proposal.word_count
            profile.save()

            # Track analytics
            execution_time = time.time() - start_time
            ProposalAnalytics.objects.create(
                user=request.user,
                action='generate',
                proposal=saved_proposal,
                metadata={
                    'proposal_type': proposal_type.name if proposal_type else 'Dynamic',
                    'papers_retrieved': rag_data['total_papers'],
                    'news_articles': rag_data.get('total_news', 0),
                    'visuals_generated': visuals['total_count'],
                    'title': title
                },
                execution_time=execution_time
            )

            # Step 5: Complete
            yield format_sse({
                'type': 'complete',
                'proposal_id': saved_proposal.id,
                'full_proposal': full_proposal_text,
                'metadata': {
                    'title': title,
                    'sections': all_sections,
                    'word_count': saved_proposal.word_count,
                    'citation_count': saved_proposal.citation_count
                },
                'bibliography': rag_data.get('bibliography', {}),
                'visuals': {
                    'count': visuals['total_count'],
                    'figures': len(visuals['figures']),
                    'tables': len(visuals['tables'])
                },
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
def proposal_detail(request, proposal_id):
    """
    Comprehensive proposal detail page with:
    - Inline editing
    - Version history
    - Export options
    - AI-powered section editing
    """
    proposal = get_object_or_404(SavedProposal, id=proposal_id, user=request.user)
    sections = proposal.sections.all().order_by('section_order')

    # Get all versions
    all_versions = SavedProposal.objects.filter(
        user=request.user,
        title=proposal.title
    ).order_by('-version')

    context = {
        'proposal': proposal,
        'sections': sections,
        'all_versions': all_versions,
        'can_edit': True,
    }

    return render(request, 'proposal_detail_comprehensive.html', context)


@login_required
@require_http_methods(["POST"])
def edit_section_with_ai(request):
    """AI-powered section editing"""
    section_id = request.POST.get('section_id')
    selected_text = request.POST.get('selected_text', '')
    instruction = request.POST.get('instruction', '')

    if not all([section_id, instruction]):
        return JsonResponse({'error': 'Section ID and instruction required'}, status=400)

    try:
        section = ProposalSection.objects.get(id=section_id, proposal__user=request.user)

        # Use OpenAI to edit the section
        generator = get_proposal_generator()
        prompt = f"""Edit the following text based on this instruction: {instruction}

Original text:
{selected_text or section.content}

Provide the edited version:"""

        response = generator.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert proposal editor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        edited_text = response.choices[0].message.content

        return JsonResponse({
            'success': True,
            'edited_text': edited_text
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def update_section_content(request):
    """Update section content manually"""
    section_id = request.POST.get('section_id')
    new_content = request.POST.get('content', '')

    if not section_id:
        return JsonResponse({'error': 'Section ID required'}, status=400)

    try:
        section = ProposalSection.objects.get(id=section_id, proposal__user=request.user)
        section.content = new_content
        section.word_count = len(new_content.split())
        section.save()

        # Update proposal word count
        proposal = section.proposal
        proposal.word_count = sum(s.word_count for s in proposal.sections.all())
        proposal.save()

        return JsonResponse({
            'success': True,
            'word_count': section.word_count
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def export_proposal(request, proposal_id, format='docx'):
    """Export proposal in various formats"""
    proposal = get_object_or_404(SavedProposal, id=proposal_id, user=request.user)
    sections = proposal.sections.all().order_by('section_order')

    export_engine = get_export_engine()

    # Prepare data
    proposal_data = {
        'title': proposal.title,
        'proposal_type': proposal.proposal_type.name if proposal.proposal_type else 'Research Proposal',
        'keywords': proposal.content_json.get('keywords', ''),
        'description': proposal.description,
        'pi_name': f"{request.user.first_name} {request.user.last_name}",
        'institution': request.user.profile.university,
        'sections': [
            {
                'name': section.section_name,
                'content': section.content,
                'word_count': section.word_count
            }
            for section in sections
        ],
        'bibliography': proposal.citations_data
    }

    # Export based on format
    if format == 'docx':
        buffer = export_engine.export_to_docx(proposal_data)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{proposal.title}.docx"'

    elif format == 'pdf':
        buffer = export_engine.export_to_pdf(proposal_data)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{proposal.title}.pdf"'

    elif format == 'latex':
        latex_content = export_engine.export_to_latex(proposal_data)
        response = HttpResponse(latex_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{proposal.title}.tex"'

    elif format == 'markdown':
        md_content = export_engine.export_to_markdown(proposal_data)
        response = HttpResponse(md_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{proposal.title}.md"'

    else:
        return JsonResponse({'error': 'Invalid format'}, status=400)

    return response


@login_required
def my_proposals(request):
    """List all proposals"""
    proposals = SavedProposal.objects.filter(
        user=request.user,
        is_latest=True
    ).order_by('-created_at')

    context = {
        'proposals': proposals
    }

    return render(request, 'my_proposals_comprehensive.html', context)


@login_required
def user_analytics(request):
    """User analytics dashboard"""
    user = request.user
    profile = user.profile

    total_proposals = SavedProposal.objects.filter(user=user).count()
    total_words = sum(p.word_count for p in SavedProposal.objects.filter(user=user))

    analytics = ProposalAnalytics.objects.filter(user=user).order_by('-created_at')[:50]

    context = {
        'profile': profile,
        'total_proposals': total_proposals,
        'total_words': total_words,
        'analytics': analytics,
    }

    return render(request, 'user_analytics_comprehensive.html', context)


def format_sse(data: dict) -> str:
    """Format data as Server-Sent Event"""
    return f"data: {json.dumps(data)}\n\n"
