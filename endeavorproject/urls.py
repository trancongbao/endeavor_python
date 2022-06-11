"""endeavorproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from endeavorapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # TODO: custom admin page
    # Deck: create, read, update (edit name, reorder, assign to users), delete
    # Card: create, read, update (rich text, <span> to mark new words, reorder cards, reorder words), delete
    # Word: create, read, update, delete (unused media also)
    path("admin/", admin.site.urls),
    path("", views.home),
    path("login/", views.login_view),
    path("logout/", views.logout_view),
    path("admin_custom/", views.admin_custom),
    path("admin_custom/create_deck/", views.create_deck),
    path("admin_custom/create_card/", views.create_card),
    path("manage_decks_access/", views.manage_decks_access),
    path("decks/", views.decks),
    path("decks/create/", views.create_deck),
    path("decks/<int:deck_id>/cards/", views.study),
    path("cards/<int:card_id>/schedule/", views.schedule),
    path("done/", views.done),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
