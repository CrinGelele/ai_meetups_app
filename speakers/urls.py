from django.urls import path

from . import views

urlpatterns = [
    path("", views.speakers_menu, name='speakers_menu_page'),
    path("page/<int:speaker_id>/", views.speaker_page, name='speaker_page'),
    path("meetup/<int:meetup_id>/", views.meetup_page, name='meetup_page'),
    path("invite_speaker/", views.invite_speaker, name='invite_speaker'),
    path("delete_meetup/", views.delete_meetup, name='delete_meetup')
]