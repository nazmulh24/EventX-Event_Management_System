from django.contrib import admin
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls
from core.views import home_view, no_permission, about_us, contact_view

from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path("events/", include("events.urls")),  # ---> Include __ events app __ urls
    path("users/", include("users.urls")),
    #
    path("", home_view, name="home"),  # --> root URL for homepage
    path("no-permission/", no_permission, name="no-permission"),
    path("about-us/", about_us, name="about_us"),
    path("contact/", contact_view, name="contact"),
] + debug_toolbar_urls()


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
