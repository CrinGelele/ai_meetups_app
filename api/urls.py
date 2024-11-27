from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('', views.UserViewSet, basename='user')

urlpatterns = [
   path('speakers/', views.SpeakersList.as_view(), name='speakers-list'),
   path('speakers/<int:speaker_id>/', views.SpeakerSingle.as_view(), name='speaker-single'),
   path('speakers/<int:speaker_id>/update_image/', views.update_speaker_image, name='speaker-image'),
   path('meetups/', views.MeetupsList.as_view(), name='meetups-list'),
   path('meetups/<int:meetup_id>/', views.MeetupSingle.as_view(), name='meetups-single'),
   path('meetups/<int:meetup_id>/submit/', views.change_status_by_user, name='meetups-submit'),
   path('meetups/<int:meetup_id>/moderate/', views.change_status_by_moderator, name='meetups-moderate'),
   path('invites/<int:meetup_id>/<int:speaker_id>/', views.InviteSingle.as_view(), name='invite-single'),
   path('users/', include(router.urls))
] 