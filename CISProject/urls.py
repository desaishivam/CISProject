"""
URL configuration for CISProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib import admin
from users import views as users_views

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='pages/main_landing_page.html'), name='home'),
    # path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('carecenter/', TemplateView.as_view(template_name='pages/carecenter.html'), name='carecenter'),
    path('cognicon/', TemplateView.as_view(template_name='pages/cognicon.html'), name='cognicon'),
    
    # Include user authentication URLs
    path('', include('users.urls')),
    
    # Include questionnaires URLs
    path('taskmanager/', include('taskmanager.urls')),
    
    # Account management URLs
    path('create-provider/', users_views.create_provider, name='create_provider'),
    path('create-patient/', users_views.create_patient, name='create_patient'),
    path('create-caregiver/', users_views.create_caregiver, name='create_caregiver'),
    
    # Account editing
    path('manage-account/<int:user_id>/', users_views.manage_account, name='manage_account'),
]
