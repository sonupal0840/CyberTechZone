from django.urls import path
from . import views

urlpatterns = [
    path('', views.lead_create_view, name='home'),  
    path('success/', views.lead_success_view, name='lead_success'),  
    path('report/', views.report_view, name='report'), 
    path('Privacy-policy/', views.privacy_view, name='Privacy-policy'), 
    path('export-leads-csv/', views.export_leads_csv, name='export_leads_csv'),  
    path('leads/', views.lead_list, name='lead_list'),  
    path('delete/<int:lead_id>/', views.delete_lead, name='delete_lead'),
    path('send-whatsapp/<int:pk>/', views.send_whatsapp_message_view, name='send_whatsapp_message'),
    path('webhook/', views.whatsapp_webhook_view, name='whatsapp_webhook'),
    path('whatsapp-sessions/', views.whatsapp_sessions_view, name='whatsapp_sessions'),
    path('whatsapp-session/', views.whatsapp_session_page, name='whatsapp_sessions'),
    path('trigger-bulk/', views.trigger_bulk_whatsapp, name='trigger_bulk_whatsapp'),

]
