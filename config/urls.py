from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Background Remover API is online!"})

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('', include('remover.urls')),
]
