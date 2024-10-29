from django.urls import path

from . import views

urlpatterns = [
    path("", views.speakers_menu, name='speakers_menu_page'),
    path("page/<int:speaker_id>/", views.speaker_page, name='speaker_page'),
    path("meetup/<int:meetup_id>/", views.meetup_page, name='meetup_page')
]