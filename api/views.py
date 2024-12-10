from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from api.serializers import SpeakerSerializer, MeetupSerializer, InviteSerializer, UserSerializer # AuthUserSerializer, AuthUserLoginSerializer, AuthUserRegisterSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from speakers.models import Speaker, Meetup, Invite, CustomUser
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.db.models import Q
from django.utils import timezone
from .minio import add_pic, process_file_remove
import os
from drf_yasg.utils import swagger_auto_schema

def get_user():
    return AuthUser.objects.filter(is_staff=False).first()

def get_moderator():
    return AuthUser.objects.filter(is_staff=True).first()

class SpeakersList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
        current_meetup = Meetup.objects.filter(user = get_user()) & Meetup.objects.filter(status = 'Черновик')
        current_meetup_id = current_meetup[0].id if current_meetup else None
        return Response({"current_meetup_id": current_meetup_id,
                         'speakers_quantity': len(Invite.objects.filter(meetup = current_meetup_id)) if current_meetup_id else None,
                         "speakers": serializer.data})
    
    @swagger_auto_schema(request_body=SpeakerSerializer)
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SpeakerSingle(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    model_class = Speaker
    serializer_class = SpeakerSerializer
    
    def get(self, request, speaker_id, format=None):
        speaker = get_object_or_404(self.model_class.objects.filter(id=speaker_id) & self.model_class.objects.filter(deletion_flag = False))
        serializer = self.serializer_class(speaker)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=SpeakerSerializer)
    def put(self, request, speaker_id, format=None):
        speaker = get_object_or_404(self.model_class, id=speaker_id)
        serializer = self.serializer_class(speaker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(request_body=SpeakerSerializer)
    def post(self, request, speaker_id, format=None):
        current_meetup = Meetup.objects.filter(user = get_user()) & Meetup.objects.filter(status = 'Черновик')
        speaker = get_object_or_404(self.model_class, id=speaker_id)
        if not current_meetup:
            meetup = Meetup(user = get_user(), creation_date = timezone.now(), status = 'Черновик')
            meetup.save()
        current_meetup = Meetup.objects.filter(user = get_user()) & Meetup.objects.filter(status = 'Черновик')
        invite = Invite(meetup = current_meetup[0], speaker = speaker)
        invite.save()
        return Response({"message":"Successfully added."})
    
    def delete(self, request, speaker_id, format=None):
        speaker = get_object_or_404(self.model_class, id=speaker_id)
        image_remove_result = process_file_remove(os.path.basename(speaker.img_url))
        if 'error' in image_remove_result.data:
            return image_remove_result
        speaker.img_url = None
        speaker.deletion_flag = True
        speaker.save()
        return Response({"message":"Successfully deleted."})

@authentication_classes([])
@api_view(["POST"])
def update_speaker_image(request, speaker_id):
    if not Speaker.objects.get(id=speaker_id):
        return Response(status=status.HTTP_404_NOT_FOUND)
    speaker = Speaker.objects.get(id=speaker_id)
    image = request.FILES.get("image")
    image_result = add_pic(speaker, image)
    if 'error' in image_result.data:    
        return image_result
    return Response(image_result.data)

class MeetupsList(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
        current_meetup = Meetup.objects.filter(user = get_user()) & Meetup.objects.filter(status = 'Черновик')
        if not current_meetup:
            return Response({"message":"No current Meetup to Confirm."})
        else:
            meetup = current_meetup[0]
            meetup.status = 'Сформирована'
            meetup.save()
            return Response({"message":"Success."})

class MeetupSingle(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    model_class = Meetup
    serializer_class = MeetupSerializer

    def get(self, request, meetup_id, format=None):
        meetup = get_object_or_404(self.model_class, id=meetup_id)
        meetup_serializer = self.serializer_class(meetup)
        meetup_speakers = Invite.objects.filter(meetup_id=meetup.id)
        speakers_serializer = InviteSerializer(meetup_speakers, many=True)
        return Response({"meetup" : meetup_serializer.data,
                         "speakers" : speakers_serializer.data})

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
    
@authentication_classes([])
@api_view(["PUT"])
def change_status_by_user(request, meetup_id):
    if not Meetup.objects.filter(id=meetup_id):
        return Response(status=status.HTTP_404_NOT_FOUND)
    meetup = Meetup.objects.get(id=meetup_id)
    if meetup.status != 'Черновик' or get_user().is_staff == True:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    meetup.status = 'Сформирована'
    meetup.submit_date = timezone.now()
    meetup.save()
    serializer = MeetupSerializer(meetup, many=False)
    return Response(serializer.data)

@authentication_classes([])
@api_view(["PUT"])
def change_status_by_moderator(request, meetup_id):
    if not Meetup.objects.filter(id=meetup_id):
        return Response(status=status.HTTP_404_NOT_FOUND)
    if 'status' not in request.data.keys():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    meetup = Meetup.objects.get(id=meetup_id)
    new_status = request.data['status']
    if meetup.status != 'Сформирована' or new_status not in ['Завершена', 'Отклонена'] or get_moderator().is_staff == False:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    meetup.status = new_status
    meetup.resolve_date = timezone.now()
    meetup.moderator = get_moderator()
    meetup.save()
    serializer = MeetupSerializer(meetup, many=False)
    return Response(serializer.data)

class InviteSingle(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    model_class = Invite
    serializer_class = InviteSerializer

    def put(self, request, meetup_id, speaker_id, format=None):
        invite = get_object_or_404(self.model_class.objects.filter(speaker_id=speaker_id), meetup_id=meetup_id)
        serializer = self.serializer_class(invite, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, meetup_id, speaker_id, format=None):
        invite = get_object_or_404(self.model_class.objects.filter(speaker_id=speaker_id), meetup_id=meetup_id)
        invite.delete()
        return Response({"message":"Successfully deleted."})
    
class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['POST'])
def login_view(request):
    username =  request.data.get('username', False)
    password =  request.data.get('password', False)
    user = authenticate(request, username=username, password=password) if username and password else None
    if user is not None:
        login(request, user)
        return Response("{'status': 'ok'}")
    else:
        return Response("{'status': 'error', 'error': 'login failed'}")

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'status': 'Success'})
        



