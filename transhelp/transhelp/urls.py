from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('trans.urls')),
    path('chart/', include('chart.urls')),
    path('admin/', admin.site.urls),
]
