# main Urls.py File 

from django.contrib import admin
from django.urls import path,include
from account import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user/', include('account.urls')),
]
