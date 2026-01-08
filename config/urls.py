from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dentist.urls')),
]

# MUHIM: Media va Static fayllar uchun (development rejimida)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin panel sarlavhalari (ixtiyoriy, lekin chiroyli ko'rinadi)
admin.site.site_header = "Stomatologiya Admin Panel"
admin.site.site_title = "Stomatologiya Admin"
admin.site.index_title = "Boshqaruv Paneli"