"""
URL configuration for apitest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import include, path


def api_home(request):
    endpoints = {
        'signup': '/api/auth/signup/',
        'login': '/api/auth/login/',
        'logout': '/api/auth/logout/',
        'reset_password': '/api/auth/reset-password/',
    }

    accept_header = request.headers.get('accept', '')
    wants_html = 'text/html' in accept_header and 'application/json' not in accept_header

    if wants_html:
        return render(request, 'accounts/dashboard.html', {
            'endpoints': endpoints,
            'user': request.user if request.user.is_authenticated else None,
        })

    return JsonResponse({
        'success': True,
        'message': 'Authentication API is available at /api/auth/',
        'endpoints': endpoints,
    })


urlpatterns = [
    path('', api_home, name='api_home'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
]
