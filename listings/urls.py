from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from listings.views import debug_cloudinary

app_name = "listings"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("activities/", views.activities, name="activities"),
    path("properties/", views.property_list, name="property_list"),
    path("properties/<slug:slug>/", views.property_detail, name="detail"),
    path("contact/<int:pk>/", views.contact_agent, name="contact_agent"),
    path('__debug_cloudinary__/', debug_cloudinary),
    path('debug-featured/', views.debug_featured, name='debug-featured'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
