from django.urls import path

from . import views

urlpatterns = [
   path('speakers/', views.SpeakersList.as_view(), name='speakers-list'),
   path('speakers/<int:speaker_id>/', views.SpeakerSingle.as_view(), name='speaker-single'),
   path('meetups/', views.MeetupsList.as_view(), name='meetups-list'),
   path('meetups/<int:meetup_id>/', views.MeetupSingle.as_view(), name='meetups-single'),
   path('invites/<int:meetup_id>/<int:speaker_id>/', views.InviteSingle.as_view(), name='invite-single')
]