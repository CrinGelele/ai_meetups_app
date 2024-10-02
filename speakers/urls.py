from django.urls import path

from . import views

urlpatterns = [
    path("", views.speakers_menu),
    path("page/", views.speaker_page),
    path("meetup/", views.meetup_page)
]