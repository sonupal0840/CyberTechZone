from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from datetime import timedelta
import json, requests
import logging
import os
import pandas as pd
from threading import Thread

from .models import Lead, WhatsAppSession
from .forms import LeadForm, LeadFilterForm
from .utils import (
    send_whatsapp,
    upload_video_get_media_id,
    handle_first_time_message,
    send_bulk_whatsapp_utility,
)

logger = logging.getLogger(__name__)

# ----------------------------------------
# Lead Views
# ----------------------------------------

def lead_create_view(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.compute_score_and_segment()
            lead.save()

            video_path = os.path.join(settings.BASE_DIR, 'static', 'media', 'whatsapp_ready.mp4')
            media_id = settings.MEDIA_ID #upload_video_get_media_id(video_path)
            logger.info(f"Phone: {lead.phone}, Media ID: {media_id}")

            if lead.phone and media_id:
                send_whatsapp(lead.phone, media_id=media_id, name_param=lead.name)
            else:
                logger.warning("WhatsApp not sent: Missing phone or media_id")

            return redirect('lead_success')
    else:
        form = LeadForm()
    return render(request, 'lead_form.html', {'form': form})

def lead_list(request):
    leads = Lead.objects.all()
    query = request.GET.get('q')
    if query:
        leads = leads.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(segment__icontains=query)
        )
    paginator = Paginator(leads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'lead_list.html', {'page_obj': page_obj})

def delete_lead(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    if request.method == 'POST':
        lead.delete()
        return redirect('lead_list')
    return render(request, 'confirm_delete.html', {'lead': lead})

def lead_success_view(request):
    return render(request, 'lead_success.html')

def privacy_view(request):
    return render(request, 'Privacy-policy.html')

def send_whatsapp_message_view(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if lead.phone:
        send_whatsapp(lead.phone, name_param=lead.name)
    return redirect('lead_list')

# ----------------------------------------
# Reports & Export
# ----------------------------------------

def report_view(request):
    leads = Lead.objects.all()
    form = LeadFilterForm(request.GET or None)
    if form.is_valid():
        interest = form.cleaned_data.get('interest')
        min_score = form.cleaned_data.get('min_score')
        max_score = form.cleaned_data.get('max_score')

        if interest:
            leads = leads.filter(interest__icontains=interest)
        if min_score is not None:
            leads = leads.filter(score__gte=min_score)
        if max_score is not None:
            leads = leads.filter(score__lte=max_score)

    paginator = Paginator(leads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'report.html', {'page_obj': page_obj, 'form': form})

def export_leads_csv(request):
    leads = Lead.objects.all()
    interest = request.GET.get('interest')
    min_score = request.GET.get('min_score')
    max_score = request.GET.get('max_score')

    if interest:
        leads = leads.filter(interest__icontains=interest)
    if min_score:
        leads = leads.filter(score__gte=min_score)
    if max_score:
        leads = leads.filter(score__lte=max_score)

    df = pd.DataFrame(list(leads.values()))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=filtered_leads.csv'
    df.to_csv(path_or_buf=response, index=False)
    return response

# ----------------------------------------
# WhatsApp Webhook
# ----------------------------------------

@csrf_exempt
@require_http_methods(["POST", "GET"])
def whatsapp_webhook_view(request):
    if request.method == 'GET':
        verify_token = settings.META_VERIFY_TOKEN
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                return HttpResponse(challenge, status=200)
            else:
                return HttpResponse("Forbidden", status=403)
        return HttpResponse("Bad Request", status=400)

    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            msg = messages[0]
            from_number = msg["from"]
            profile = value.get("contacts", [{}])[0].get("profile", {})
            name = profile.get("name", "User")

            handle_first_time_message(from_number, name)

        return HttpResponse("EVENT_RECEIVED", status=200)

# ----------------------------------------
# WhatsApp Session History View
# ----------------------------------------

def whatsapp_sessions_view(request):
    filter_option = request.GET.get('filter', 'all')
    sessions = WhatsAppSession.objects.all()

    if filter_option == 'today':
        sessions = sessions.filter(last_message_at__date=now().date())
    elif filter_option == '7days':
        sessions = sessions.filter(last_message_at__gte=now() - timedelta(days=7))
    elif filter_option == '30days':
        sessions = sessions.filter(last_message_at__gte=now() - timedelta(days=30))

    sessions = sessions.order_by('-last_message_at')
    return render(request, 'whatsapp_sessions.html', {
        'sessions': sessions,
        'selected': filter_option
    })
    
def delete_whatsapp_session(request, session_id):
    session = get_object_or_404(WhatsAppSession, id=session_id)
    if request.method == "POST":
        session.delete()
        return redirect('whatsapp_sessions')  # wahi view jisme tum list dikha rahe ho

# ----------------------------------------
# API: Bulk Text Message Trigger
# ----------------------------------------

@csrf_exempt
def trigger_bulk_whatsapp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            numbers = data.get("numbers", [])
            message = data.get("message", "Hello from CyberTechZone Funnel")

            if not numbers or not isinstance(numbers, list):
                return JsonResponse({"error": "Invalid phone numbers"}, status=400)

            Thread(target=send_bulk_whatsapp_utility, args=(numbers, message)).start()
            return JsonResponse({"status": "Bulk messaging initiated"}, status=200)
        except Exception as e:
            logger.error(f"[API] Bulk message error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

# ----------------------------------------
# Test Page for Sessions
# ----------------------------------------

def whatsapp_session_page(request):
    filter_option = request.GET.get('filter', 'all')
    sessions = WhatsAppSession.objects.all()

    if filter_option == 'today':
        sessions = sessions.filter(last_message_at__date=now().date())
    elif filter_option == '7days':
        sessions = sessions.filter(last_message_at__gte=now() - timedelta(days=7))
    elif filter_option == '30days':
        sessions = sessions.filter(last_message_at__gte=now() - timedelta(days=30))

    sessions = sessions.order_by('-last_message_at')

    return render(request, 'whatsapp_session.html', {
        'sessions': sessions,
        'selected': filter_option
    })

