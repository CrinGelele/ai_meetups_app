from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from api.serializers import SpeakerSerializer, MeetupSerializer, InviteSerializer
from django.contrib.auth import get_user_model
from speakers.models import Speaker, Meetup, Invite, AuthUser
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.db.models import Q
from django.utils import timezone

def get_current_user():
    try:
        user = AuthUser.objects.get(id=2)
    except:
        user = AuthUser(first_name="Макс", last_name="Сергеев", password='cringe', username='cringelele')
        user.save()
    return user

class SpeakersList(APIView):
    model_class = Speaker
    serializer_class = SpeakerSerializer
    
    def get(self, request, format="None"):
        speaker_name_to_find = request.GET.get('speaker_name_to_find')
        speakers = self.model_class.objects.filter(~Q(deletion_flag = True)) if not speaker_name_to_find else self.model_class.objects.filter(
            ~Q(deletion_flag = True)) & (
                self.model_class.objects.filter(first_name__icontains = speaker_name_to_find
                                                ) | self.model_class.objects.filter(last_name__icontains = speaker_name_to_find)
                                        )
        serializer = self.serializer_class(speakers, many=True)
        current_meetup = Meetup.objects.filter(user = get_current_user()) & Meetup.objects.filter(status = 'Черновик')
        current_meetup_id = current_meetup[0].id if current_meetup else None
        return Response({"current_meetup_id": current_meetup_id,
                         'speakers_quantity': len(Invite.objects.filter(meetup = current_meetup_id)) if current_meetup_id else None,
                         "speakers": serializer.data})
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SpeakerSingle(APIView):
    model_class = Speaker
    serializer_class = SpeakerSerializer
    
    def get(self, request, speaker_id, format=None):
        speaker = get_object_or_404(self.model_class.objects.filter(id=speaker_id) & self.model_class.objects.filter(deletion_flag = False))
        serializer = self.serializer_class(speaker)
        return Response(serializer.data)

    def put(self, request, speaker_id, format=None):
        speaker = get_object_or_404(self.model_class, id=speaker_id)
        serializer = self.serializer_class(speaker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, speaker_id, format=None):
        current_meetup = Meetup.objects.filter(user = get_current_user()) & Meetup.objects.filter(status = 'Черновик')
        speaker = get_object_or_404(self.model_class, id=speaker_id)
        if not current_meetup:
            meetup = Meetup(user = get_current_user(), creation_date = timezone.now(), status = 'Черновик')
            meetup.save()
        current_meetup = Meetup.objects.filter(user = get_current_user()) & Meetup.objects.filter(status = 'Черновик')
        invite = Invite(meetup = current_meetup[0], speaker = speaker)
        invite.save()
        return Response({"message":"Successfully added."})
    
    def delete(self, request, speaker_id, format=None):
        speaker = get_object_or_404(self.model_class, id=speaker_id)
        speaker.deletion_flag = True
        speaker.save()
        return Response({"message":"Successfully deleted."})

class MeetupsList(APIView):
    model_class = Meetup
    serializer_class = MeetupSerializer

    def get(self, request, format=None):
        status = request.GET.get('status', '')
        start = request.GET.get('start')
        end = request.GET.get('end')
        if start and end:
            meetups = self.model_class.objects.filter(~Q(status="Черновик") & ~Q(status="Удалена") & Q(status__contains=status)
                                                    & (Q(submit_date__range = (start, end)))
                                                    )
        else:
            meetups = self.model_class.objects.filter(~Q(status="Черновик") & ~Q(status="Удалена") & Q(status__contains=status))
        serializer = self.serializer_class(meetups, many=True)
        return Response(serializer.data)
    
    def put(self, reques, format=None):
        current_meetup = Meetup.objects.filter(user = get_current_user()) & Meetup.objects.filter(status = 'Черновик')
        if not current_meetup:
            return Response({"message":"No current Meetup to Confirm."})
        else:
            meetup = current_meetup[0]
            meetup.status = 'Сформирована'
            meetup.save()
            return Response({"message":"Success."})

class MeetupSingle(APIView):
    model_class = Meetup
    serializer_class = MeetupSerializer

    def put(self, request, meetup_id, format=None):
        meetup = get_object_or_404(self.model_class, id=meetup_id)
        serializer = self.serializer_class(meetup, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, meetup_id, format=None):
        meetup = get_object_or_404(self.model_class, id=meetup_id)
        meetup.status = 'Удалена'
        meetup.submit_date = timezone.now()
        meetup.save()
        return Response({"message":"Successfully deleted."})


class InviteSingle(APIView):
    model_class = Invite
    serializer_class = InviteSerializer

    def put(self, request, meetup_id, speaker_id, format=None):
        invite = get_object_or_404(self.model_class.objects.filter(speaker_id=speaker_id), meetup_id=meetup_id)
        invite.approx_perfomance_duration = request.GET.get('approx_perfomance_duration')
        serializer = self.serializer_class(invite, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, meetup_id, speaker_id, format=None):
        invite = get_object_or_404(self.model_class.objects.filter(speaker_id=speaker_id), meetup_id=meetup_id)
        invite.delete()
        return Response({"message":"Successfully deleted."})

