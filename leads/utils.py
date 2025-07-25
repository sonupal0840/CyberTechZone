import requests
import json
import os
import logging
import threading
from threading import Timer
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from .models import WhatsAppSession, MessageLog

logger = logging.getLogger(__name__)

# ----------------------------------------
# ✅ Video Upload Utility (Old Flow)
# ----------------------------------------
def upload_video_get_media_id(file_path):
    if not os.path.exists(file_path):
        logger.error(f"❌ Video file not found: {file_path}")
        return None

    logger.info(f"📂 Uploading file: {file_path}")

    url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/media"
    headers = {
        "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}"
    }

    with open(file_path, 'rb') as file_obj:
        files = {
            'file': (os.path.basename(file_path), file_obj, 'video/mp4'),
            'messaging_product': (None, 'whatsapp')
        }

        response = requests.post(url, headers=headers, files=files)
        logger.info(f"📤 Upload Status: {response.status_code}")
        logger.info(f"📤 Upload Response: {response.text}")

        if response.status_code == 200:
            media_id = response.json().get('id')
            logger.info(f"✅ Media uploaded. ID: {media_id}")
            return media_id
        else:
            logger.error(f"❌ Failed to upload media. Status: {response.status_code}, Response: {response.text}")
            return None

# ----------------------------------------
# ✅ Send WhatsApp (Old template - video)
# ----------------------------------------
def send_whatsapp(phone_number, media_id=None, name_param=None, template_type='initial'):
    url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    template_data = {
        "name": "confirmation_video",
        "language": {"code": "en_US"},
        "components": []
    }

    if media_id:
        template_data["components"].append({
            "type": "header",
            "parameters": [{
                "type": "video",
                "video": {"id": media_id}
            }]
        })

    name_text = name_param or "User"
    template_data["components"].append({
        "type": "body",
        "parameters": [{"type": "text", "text": name_text}]
    })

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": template_data
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        status = "sent" if response.status_code == 200 else "failed"
        logger.info(f"✅ WhatsApp to {phone_number}: {response.status_code} {response.text}")
    except Exception as e:
        status = "failed"
        logger.error(f"❌ WhatsApp Error: {str(e)}")

    MessageLog.objects.create(
        phone=phone_number,
        name=name_param or "User",
        template_type=template_type,
        status=status
    )

# ----------------------------------------
# ✅ First-time Message Auto Handler
# ----------------------------------------
def handle_first_time_message(phone_number, name="User"):
    session, created = WhatsAppSession.objects.get_or_create(phone=phone_number)

    if created or now() - session.last_message_at > timedelta(hours=24):
        video_path = os.path.join(settings.BASE_DIR, 'static', 'media', 'whatsapp_ready.mp4')
        media_id = upload_video_get_media_id(video_path)
        if phone_number and media_id:
            send_whatsapp(phone_number, media_id=media_id, name_param=name, template_type='initial')
            schedule_followups(phone_number, name, media_id)

    session.last_message_at = now()
    session.save()

# ----------------------------------------
# ✅ Schedule Followups
# ----------------------------------------
def schedule_followups(phone_number, name, media_id):
    try:
        Timer(900, send_whatsapp, args=[phone_number], kwargs={
            "media_id": media_id, "name_param": name, "template_type": "followup1"
        }).start()
        logger.info(f"🕒 15-min follow-up scheduled for {phone_number}")

        Timer(3600, send_whatsapp, args=[phone_number], kwargs={
            "media_id": media_id, "name_param": name, "template_type": "followup2"
        }).start()
        logger.info(f"🕒 1-hour follow-up scheduled for {phone_number}")
    except Exception as e:
        logger.error(f"❌ Error in follow-up scheduler: {str(e)}")

# ----------------------------------------
# ✅ Plain Text Utility Sender (Bulk)
# ----------------------------------------
def send_bulk_whatsapp_utility(numbers, message):
    url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    for number in numbers:
        payload = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "text",
            "text": {"body": message}
        }
        try:
            res = requests.post(url, headers=headers, json=payload)
            logger.info(f"[UTILITY] ✉️ Message to {number}: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"[UTILITY] ❌ Failed to send to {number}: {str(e)}")