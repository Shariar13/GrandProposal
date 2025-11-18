from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
import json
from .generators import ProposalGenerator
from .llm_enhance import ProposalEnhancer

generator_instance = None
enhancer_instance = None


def get_generator():
    global generator_instance
    if generator_instance is None:
        generator_instance = ProposalGenerator()
    return generator_instance


def get_enhancer():
    global enhancer_instance
    if enhancer_instance is None:
        enhancer_instance = ProposalEnhancer()
    return enhancer_instance


def home(request):
    return render(request, 'index.html')


def generate_proposal_stream(request):
    if request.method != 'POST':
        return StreamingHttpResponse(
            json.dumps({
                "type": "error", 
                "content": "POST method required. Please submit the form properly."
            }) + "\n",
            content_type='text/event-stream'
        )
    
    title = request.POST.get('title', '').strip()
    keywords = request.POST.get('keywords', '').strip()
    description = request.POST.get('description', '').strip()
    
    if not title or not description:
        return StreamingHttpResponse(
            json.dumps({
                "type": "error", 
                "content": "Title and description are required fields. Please provide both to generate a comprehensive proposal."
            }) + "\n",
            content_type='text/event-stream'
        )
    
    if len(description.split()) < 10:
        return StreamingHttpResponse(
            json.dumps({
                "type": "error", 
                "content": "Please provide a more detailed description (minimum 10 words recommended). More detail results in higher quality, more specific proposals."
            }) + "\n",
            content_type='text/event-stream'
        )
    
    if not keywords:
        keywords = title
    
    def event_stream():
        try:
            gen = get_generator()
            for chunk in gen.generate_full_proposal(title, keywords, description):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = json.dumps({
                "type": "error", 
                "content": f"Generation error: {str(e)}"
            })
            yield f"data: {error_msg}\n\n"
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


def enhance_proposal_stream(request):
    if request.method != 'POST':
        return JsonResponse({
            "error": "POST method required"
        }, status=405)
    
    original_proposal = request.POST.get('proposal_content', '').strip()
    
    if not original_proposal:
        return JsonResponse({
            "error": "No proposal content provided"
        }, status=400)
    
    if len(original_proposal) < 500:
        return JsonResponse({
            "error": "Proposal too short. Generate a full RAG proposal first."
        }, status=400)
    
    def event_stream():
        try:
            enhancer = get_enhancer()
            for chunk in enhancer.enhance_full_proposal(original_proposal):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = json.dumps({
                "type": "error",
                "content": f"Enhancement error: {str(e)}"
            })
            yield f"data: {error_msg}\n\n"
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response