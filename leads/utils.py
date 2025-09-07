# import requests
# import json
# import os
# import logging
# import threading
# from threading import Timer
# from django.conf import settings
# from django.utils.timezone import now
# from datetime import timedelta
# from .models import WhatsAppSession, MessageLog

# logger = logging.getLogger(__name__)

# # ----------------------------------------
# # ✅ Video Upload Utility (Old Flow)
# # ----------------------------------------
# def upload_video_get_media_id(file_path):
#     if not os.path.exists(file_path):
#         logger.error(f"❌ Video file not found: {file_path}")
#         return None

#     logger.info(f"📂 Uploading file: {file_path}")

#     url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/media"
#     headers = {
#         "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}"
#     }

#     with open(file_path, 'rb') as file_obj:
#         files = {
#             'file': (os.path.basename(file_path), file_obj, 'video/mp4'),
#             'messaging_product': (None, 'whatsapp')
#         }

#         response = requests.post(url, headers=headers, files=files)
#         logger.info(f"📤 Upload Status: {response.status_code}")
#         logger.info(f"📤 Upload Response: {response.text}")

#         if response.status_code == 200:
#             media_id = response.json().get('id')
#             logger.info(f"✅ Media uploaded. ID: {media_id}")
#             return media_id
#         else:
#             logger.error(f"❌ Failed to upload media. Status: {response.status_code}, Response: {response.text}")
#             return None
        
        
# def upload_image_get_media_id(file_path):
#     if not os.path.exists(file_path):
#         logger.error(f"❌ Image file not found: {file_path}")
#         return None

#     url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/media"
#     headers = {"Authorization": f"Bearer {settings.META_ACCESS_TOKEN}"}

#     with open(file_path, 'rb') as file_obj:
#         files = {
#             'file': (os.path.basename(file_path), file_obj, 'image/png'),
#             'messaging_product': (None, 'whatsapp')
#         }
#         response = requests.post(url, headers=headers, files=files)
#         logger.info(f"📤 Image Upload: {response.status_code} {response.text}")

#         if response.status_code == 200:
#             return response.json().get("id")
#         return None



    
    
# def send_whatsapp(phone_number, media_id=None, name_param=None, template_type='initial'):
#     url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/messages"
#     headers = {
#         "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }

#     payload = {}

#     if template_type == "initial":
#         # पहला message = template + video
#         template_data = {
#             "name": "confirmation_video",
#             "language": {"code": "en_US"},
#             "components": []
#         }
#         if media_id:
#             template_data["components"].append({
#                 "type": "header",
#                 "parameters": [{"type": "video", "video": {"id": media_id}}]
#             })
#         template_data["components"].append({
#             "type": "body",
#             "parameters": [{"type": "text", "text": name_param or "User"}]
#         })

#         payload = {
#             "messaging_product": "whatsapp",
#             "to": phone_number,
#             "type": "template",
#             "template": template_data
#         }

#     elif template_type == "followup1":
#         # दूसरा message = केवल text
#         payload = {
#             "messaging_product": "whatsapp",
#             "to": phone_number,
#             "type": "text",
#             "text": {"body": f"Hi {name_param}, ⚠️ Urgent Update : To buy the full course visit my instagram channel"}
#         }

#     elif template_type == "followup2":
#         # तीसरा message = image + caption
#         img_path = os.path.join(settings.BASE_DIR, 'static', 'media', 'image.png')
#         img_media_id = upload_image_get_media_id(img_path)

#         if img_media_id:
#             payload = {
#                 "messaging_product": "whatsapp",
#                 "to": phone_number,
#                 "type": "image",
#                 "image": {
#                     "id": img_media_id,
#                     "caption": f"Hey {name_param}, 🎉 Congratulations subsidy form was active so I have filled it on my student behalf"
#                 }
#             }
#         else:
#             logger.error("❌ Could not upload image for followup2.")
#             return

#     try:
#         response = requests.post(url, headers=headers, data=json.dumps(payload))
#         status = "sent" if response.status_code == 200 else "failed"
#         logger.info(f"✅ WhatsApp to {phone_number} ({template_type}): {response.status_code} {response.text}")
#     except Exception as e:
#         status = "failed"
#         logger.error(f"❌ WhatsApp Error: {str(e)}")

#     MessageLog.objects.create(
#         phone=phone_number,
#         name=name_param or "User",
#         template_type=template_type,
#         status=status
#     )


# # ----------------------------------------
# # ✅ First-time Message Auto Handler
# # ----------------------------------------
# def handle_first_time_message(phone_number, name="User"):
#     session, created = WhatsAppSession.objects.get_or_create(phone=phone_number)

#     if created or now() - session.last_message_at > timedelta(hours=24):
#         video_path = os.path.join(settings.BASE_DIR, 'static', 'media', 'whatsapp_ready.mp4')
#         media_id = upload_video_get_media_id(video_path)
#         if phone_number and media_id:
#             send_whatsapp(phone_number, media_id=media_id, name_param=name, template_type='initial')
#             schedule_followups(phone_number, name, media_id)

#     session.last_message_at = now()
#     session.save()

# # ----------------------------------------
# # ✅ Schedule Followups
# # ----------------------------------------
# def schedule_followups(phone_number, name, media_id):
#     try:
#         Timer(900, send_whatsapp, args=[phone_number], kwargs={
#             "media_id": media_id, "name_param": name, "template_type": "followup1"
#         }).start()
#         logger.info(f"🕒 15-min follow-up scheduled for {phone_number}")

#         Timer(3600, send_whatsapp, args=[phone_number], kwargs={
#             "media_id": media_id, "name_param": name, "template_type": "followup2"
#         }).start()
#         logger.info(f"🕒 1-hour follow-up scheduled for {phone_number}")
#     except Exception as e:
#         logger.error(f"❌ Error in follow-up scheduler: {str(e)}")

# # ----------------------------------------
# # ✅ Plain Text Utility Sender (Bulk)
# # ----------------------------------------
# def send_bulk_whatsapp_utility(numbers, message):
#     url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/messages"
#     headers = {
#         "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
#         "Content-Type": "application/json"
#     }
#     for number in numbers:
#         payload = {
#             "messaging_product": "whatsapp",
#             "to": number,
#             "type": "text",
#             "text": {"body": message}
#         }
#         try:
#             res = requests.post(url, headers=headers, json=payload)
#             logger.info(f"[UTILITY] ✉️ Message to {number}: {res.status_code} {res.text}")
#         except Exception as e:
#             logger.error(f"[UTILITY] ❌ Failed to send to {number}: {str(e)}")
            
'''___________________________________________________________________________________________________________________'''

import requests
import json
import os
import logging
from threading import Timer
from django.conf import settings
from django.utils.timezone import now
from django.core.cache import cache
from datetime import timedelta
from .models import WhatsAppSession, MessageLog

logger = logging.getLogger(__name__)


# ----------------------------------------
# ✅ Upload Video and Get Media ID
# ----------------------------------------
def upload_video_get_media_id(file_path):
    if not os.path.exists(file_path):
        logger.error(f"❌ Video file not found: {file_path}")
        return None

    url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/media"
    headers = {"Authorization": f"Bearer {settings.META_ACCESS_TOKEN}"}

    with open(file_path, "rb") as file_obj:
        files = {
            "file": (os.path.basename(file_path), file_obj, "video/mp4"),
            "messaging_product": (None, "whatsapp"),
        }

        response = requests.post(url, headers=headers, files=files)
        logger.info(f"📤 Upload Status: {response.status_code}")
        logger.info(f"📤 Upload Response: {response.text}")

        if response.status_code == 200:
            media_id = response.json().get("id")
            logger.info(f"✅ Media uploaded. ID: {media_id}")
            return media_id
        else:
            logger.error(
                f"❌ Failed to upload media. Status: {response.status_code}, Response: {response.text}"
            )
            return None


# ----------------------------------------
# ✅ Upload Image and Get Media ID
# ----------------------------------------
def upload_image_get_media_id(file_path):
    if not os.path.exists(file_path):
        logger.error(f"❌ Image file not found: {file_path}")
        return None

    url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/media"
    headers = {"Authorization": f"Bearer {settings.META_ACCESS_TOKEN}"}

    with open(file_path, "rb") as file_obj:
        files = {
            "file": (os.path.basename(file_path), file_obj, "image/png"),
            "messaging_product": (None, "whatsapp"),
        }
        response = requests.post(url, headers=headers, files=files)
        logger.info(f"📤 Image Upload: {response.status_code} {response.text}")

        if response.status_code == 200:
            return response.json().get("id")
        return None


# ----------------------------------------
# ✅ Cached Media ID Loader
# ----------------------------------------
def get_cached_media_id():
    cache_key = "WHATSAPP_VIDEO_MEDIA_ID"
    media_id = cache.get(cache_key)

    if media_id:
        return media_id

    # DB fallback
    last_log = (
        MessageLog.objects.filter(template_type="initial", status="sent")
        .exclude(media_id__isnull=True)
        .order_by("-created_at")
        .first()
    )
    if last_log and hasattr(last_log, "media_id") and last_log.media_id:
        cache.set(cache_key, last_log.media_id, timeout=86400 * 29)
        return last_log.media_id

    # Upload new
    video_path = os.path.join(
        settings.BASE_DIR, "static", "media", "whatsapp_ready.mp4"
    )
    media_id = upload_video_get_media_id(video_path)
    if media_id:
        cache.set(cache_key, media_id, timeout=86400 * 29)
    return media_id


# ----------------------------------------
# ✅ Send WhatsApp Message
# ----------------------------------------
def send_whatsapp(phone_number, media_id=None, name_param=None, template_type="initial"):
    url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {}

    if template_type == "initial":
        template_data = {
            "name": "confirmation_video",
            "language": {"code": "en_US"},
            "components": [],
        }
        if media_id:
            template_data["components"].append(
                {
                    "type": "header",
                    "parameters": [{"type": "video", "video": {"id": media_id}}],
                }
            )
        template_data["components"].append(
            {
                "type": "body",
                "parameters": [{"type": "text", "text": name_param or "User"}],
            }
        )

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": template_data,
        }

    elif template_type == "followup1":
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": f"Hi {name_param}, ⚠️ Urgent Update: To buy the full course visit my Instagram channel"
            },
        }

    elif template_type == "followup2":
        img_path = os.path.join(settings.BASE_DIR, "static", "media", "image.png")
        img_media_id = upload_image_get_media_id(img_path)

        if img_media_id:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "image",
                "image": {
                    "id": img_media_id,
                    "caption": f"Hey {name_param}, 🎉 Congratulations! Subsidy form was active so I filled it for my student.",
                },
            }
        else:
            logger.error("❌ Could not upload image for followup2.")
            return

    # Send request
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        status = "sent" if response.status_code == 200 else "failed"
        logger.info(
            f"✅ WhatsApp to {phone_number} ({template_type}): {response.status_code} {response.text}"
        )
    except Exception as e:
        status = "failed"
        logger.error(f"❌ WhatsApp Error: {str(e)}")

    # Save log (without media_id if not in model)
    log_data = {
        "phone": phone_number,
        "name": name_param or "User",
        "template_type": template_type,
        "status": status,
    }
    if hasattr(MessageLog, "media_id") and media_id:
        log_data["media_id"] = media_id

    MessageLog.objects.create(**log_data)


# ----------------------------------------
# ✅ First-time Handler
# ----------------------------------------
def handle_first_time_message(phone_number, name="User"):
    session, created = WhatsAppSession.objects.get_or_create(phone=phone_number)

    if created or now() - session.last_message_at > timedelta(hours=24):
        media_id = get_cached_media_id()
        if phone_number and media_id:
            send_whatsapp(
                phone_number, media_id=media_id, name_param=name, template_type="initial"
            )
            schedule_followups(phone_number, name, media_id)

    session.last_message_at = now()
    session.save()


# ----------------------------------------
# ✅ Followups Scheduler
# ----------------------------------------
def schedule_followups(phone_number, name, media_id):
    try:
        Timer(
            90,
            send_whatsapp,
            args=[phone_number],
            kwargs={
                "media_id": media_id,
                "name_param": name,
                "template_type": "followup1",
            },
        ).start()
        logger.info(f"🕒 15-min follow-up scheduled for {phone_number}")

        Timer(
            100,
            send_whatsapp,
            args=[phone_number],
            kwargs={
                "media_id": media_id,
                "name_param": name,
                "template_type": "followup2",
            },
        ).start()
        logger.info(f"🕒 1-hour follow-up scheduled for {phone_number}")
    except Exception as e:
        logger.error(f"❌ Error in follow-up scheduler: {str(e)}")


# ----------------------------------------
# ✅ Bulk Sender
# ----------------------------------------
def send_bulk_whatsapp_utility(numbers, message):
    url = f"https://graph.facebook.com/v19.0/{settings.META_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.META_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    for number in numbers:
        payload = {
            "messaging_product": "whatsapp",
            "to": number,
            "type": "text",
            "text": {"body": message},
        }
        try:
            res = requests.post(url, headers=headers, json=payload)
            logger.info(f"[UTILITY] ✉️ Message to {number}: {res.status_code} {res.text}")
        except Exception as e:
            logger.error(f"[UTILITY] ❌ Failed to send to {number}: {str(e)}")
