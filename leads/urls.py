from django.urls import path
from django.urls import path
from .views import dashboard, add_purchase,lead_list,lead_report, lead_detail , user_login,delete_lead, user_logout, user_register, whatsapp_webhook, home,create_lead, update_lead
from . import views


urlpatterns = [
    path("home/", home, name="home"),  # Avoid conflict with the root URL in project-level urls.py
    path("dashboard/", dashboard, name="dashboard"),
    path("whatsapp/", whatsapp_webhook, name="whatsapp_webhook"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("register/", user_register, name="register"), 
    path("create/", create_lead, name="create_lead"),
    path("update/<int:pk>/", update_lead, name="update_lead"),
    path("delete/<int:pk>/", delete_lead, name="delete_lead"),
    path("list/", lead_list, name="lead_list"),
    path("<int:pk>/", lead_detail, name="lead_detail"),
    path('report/', lead_report, name='lead_report'),
    path('add-purchase/', add_purchase, name='add_purchase'),
    
]

