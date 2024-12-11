from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from api.serializers import SpeakerSerializer, MeetupSerializer, InviteSerializer, UserSerializer
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
from drf_yasg import openapi
from django.conf import settings
import redis
import uuid
from rest_framework import permissions

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return None

def get_user(request):
    session_id = request.COOKIES.get('session_id', None)
    user_username = session_storage.get(session_id) if session_id else None
    return CustomUser.objects.get(username=user_username) if user_username else None
    
class IsGuest(permissions.BasePermission):
    def has_permission(self, request, view):
        return False if get_user(request) else True

class IsAuthentificated(permissions.BasePermission):
    def has_permission(self, request, view):
        return True if get_user(request) else False

class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(get_user(request) and not get_user(request).is_staff and not get_user(request).is_superuser)

class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(get_user(request) and get_user(request).is_staff)

class AllowAny(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
    
def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes        
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator

class SpeakersList(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    model_class = Speaker
    serializer_class = SpeakerSerializer
    
    @swagger_auto_schema(operation_id="read_speakers_list", operation_description="Получить список спикеров", tags=["Speakers"])
    @method_permission_classes((AllowAny,))
    def get(self, request, format="None"):
        speaker_name_to_find = request.GET.get('speaker_name_to_find')
        speakers = self.model_class.objects.filter(~Q(deletion_flag = True)) if not speaker_name_to_find else self.model_class.objects.filter(
            ~Q(deletion_flag = True)) & (
                self.model_class.objects.filter(first_name__icontains = speaker_name_to_find
                                                ) | self.model_class.objects.filter(last_name__icontains = speaker_name_to_find)
                                        )
        serializer = self.serializer_class(speakers, many=True)
        current_meetup = Meetup.objects.filter(user = get_user(request)) & Meetup.objects.filter(status = 'Черновик')
        current_meetup_id = current_meetup[0].id if current_meetup else None
        return Response({"current_meetup_id": current_meetup_id,
                         'speakers_quantity': len(Invite.objects.filter(meetup = current_meetup_id)) if current_meetup_id else None,
                         "speakers": serializer.data})
    
    @swagger_auto_schema(operation_id="create_speaker", operation_description="Добавить нового спикера", request_body=SpeakerSerializer, tags=["Speakers"])
    @method_permission_classes((IsModerator))
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SpeakerSingle(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    model_class = Speaker
    serializer_class = SpeakerSerializer
    
    @swagger_auto_schema(operation_id="read_single_speaker", operation_description="Получить информацию о спикере", tags=["Speakers"])
    @method_permission_classes((AllowAny,))
    def get(self, request, speaker_id, format=None):
        speaker = get_object_or_404(self.model_class.objects.filter(id=speaker_id) & self.model_class.objects.filter(deletion_flag = False))
        serializer = self.serializer_class(speaker)
        return Response(serializer.data)
    
    @swagger_auto_schema(operation_id="edit_single_speaker", request_body=SpeakerSerializer, operation_description="Изменить информацию о спикере", tags=["Speakers"])
    @method_permission_classes((IsModerator))
    def put(self, request, speaker_id, format=None):
        speaker = get_object_or_404(self.model_class, id=speaker_id)
        serializer = self.serializer_class(speaker, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_id="invite_single_speaker", operation_description="Пригласить спикера на митап", tags=["Speakers"])
    @method_permission_classes((IsUser,))
    def post(self, request, speaker_id, format=None):
        current_meetup = Meetup.objects.filter(user = get_user(request)) & Meetup.objects.filter(status = 'Черновик')
        speaker = get_object_or_404(self.model_class, id=speaker_id)
        if not current_meetup:
            meetup = Meetup(user = get_user(request), creation_date = timezone.now(), status = 'Черновик')
            meetup.save()
        current_meetup = Meetup.objects.filter(user = get_user(request)) & Meetup.objects.filter(status = 'Черновик')
        invite = Invite(meetup = current_meetup[0], speaker = speaker)
        invite.save()
        return Response({"message":"Successfully added."})
    
    @swagger_auto_schema(operation_id="delete_single_speaker", operation_description="Удалить данные о спикере", tags=["Speakers"])
    @method_permission_classes((IsModerator,))
    def delete(self, request, speaker_id, format=None):
        speaker = get_object_or_404(self.model_class, id=speaker_id)
        image_remove_result = process_file_remove(os.path.basename(speaker.img_url))
        if 'error' in image_remove_result.data:
            return image_remove_result
        speaker.img_url = None
        speaker.deletion_flag = True
        speaker.save()
        return Response({"message":"Successfully deleted."})


@csrf_exempt
@swagger_auto_schema(method='post', operation_id="add_speaker_photo", operation_description="Добавить фото спикера", tags=["Speakers"])
@api_view(['POST'])
@permission_classes([IsModerator])
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
    authentication_classes = [CsrfExemptSessionAuthentication]
    model_class = Meetup
    serializer_class = MeetupSerializer

    @swagger_auto_schema(operation_id="get_meetups_list", operation_description="Получить список митапов", tags=["Meetups"])
    @method_permission_classes((IsModerator,))
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
    
    @swagger_auto_schema(operation_id="submit_current_meetup", operation_description="Сформировать митап текущего пользователя", tags=["Meetups"])
    @method_permission_classes((IsUser,))
    def put(self, request, format=None):
        current_meetup = Meetup.objects.filter(user = get_user(request)) & Meetup.objects.filter(status = 'Черновик')
        if not current_meetup:
            return Response({"message":"No current Meetup to Confirm."})
        else:
            meetup = current_meetup[0]
            meetup.status = 'Сформирована'
            meetup.save()
            return Response({"message":"Success."})

class MeetupSingle(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    model_class = Meetup
    serializer_class = MeetupSerializer

    @swagger_auto_schema(operation_id="get_single_meetup", operation_description="Получить информацию о митапе", tags=["Meetups"])
    @method_permission_classes((IsUser, IsModerator))
    def get(self, request, meetup_id, format=None):
        meetup = get_object_or_404(self.model_class, id=meetup_id)
        meetup_serializer = self.serializer_class(meetup)
        meetup_speakers = Invite.objects.filter(meetup_id=meetup.id)
        speakers_serializer = InviteSerializer(meetup_speakers, many=True)
        return Response({"meetup" : meetup_serializer.data,
                         "speakers" : speakers_serializer.data})

    @swagger_auto_schema(operation_id="change_single_meetup", request_body=MeetupSerializer, operation_description="Изменить информацию о митапе", tags=["Meetups"])
    @method_permission_classes((IsUser, IsModerator))
    def put(self, request, meetup_id, format=None):
        meetup = get_object_or_404(self.model_class, id=meetup_id)
        serializer = self.serializer_class(meetup, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(operation_id="delete_single_meetup", request_body=MeetupSerializer, operation_description="Удалить информацию о митапе", tags=["Meetups"])
    @method_permission_classes((IsUser))
    def delete(self, request, meetup_id, format=None):
        meetup = get_object_or_404(self.model_class, id=meetup_id)
        if meetup.user != get_user(request):
            return Response({"message":"Not yours"})
        meetup.status = 'Удалена'
        meetup.submit_date = timezone.now()
        meetup.save()
        return Response({"message":"Successfully deleted."})
    
@csrf_exempt
@swagger_auto_schema(method='put', operation_id="submit_meetup", operation_description="Сформировать митап", tags=['Meetups'])
@api_view(['PUT'])
@permission_classes([IsUser])
def change_status_by_user(request, meetup_id):
    if not Meetup.objects.filter(id=meetup_id):
        return Response(status=status.HTTP_404_NOT_FOUND)
    meetup = Meetup.objects.get(id=meetup_id)
    if meetup.status != 'Черновик' or get_user(request).is_staff == True:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    meetup.status = 'Сформирована'
    meetup.submit_date = timezone.now()
    meetup.save()
    serializer = MeetupSerializer(meetup, many=False)
    return Response(serializer.data)

@csrf_exempt
@swagger_auto_schema(method='put', operation_id="moderate_meetup", operation_description="Модерировать митап", tags=['Meetups'])
@api_view(['PUT'])
@permission_classes([IsModerator])
def change_status_by_moderator(request, meetup_id):
    if not Meetup.objects.filter(id=meetup_id):
        return Response(status=status.HTTP_404_NOT_FOUND)
    if 'status' not in request.data.keys():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    meetup = Meetup.objects.get(id=meetup_id)
    new_status = request.data['status']
    if meetup.status != 'Сформирована' or new_status not in ['Завершена', 'Отклонена'] or get_user(request).is_staff == False:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    meetup.status = new_status
    meetup.resolve_date = timezone.now()
    meetup.moderator = get_user(request)
    meetup.save()
    serializer = MeetupSerializer(meetup, many=False)
    return Response(serializer.data)

class InviteSingle(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    model_class = Invite
    serializer_class = InviteSerializer

    @swagger_auto_schema(operation_id="change_single_invite", request_body=InviteSerializer, operation_description="Изменить приглашение", tags=["Invites"])
    @method_permission_classes((IsUser, IsModerator))
    def put(self, request, meetup_id, speaker_id, format=None):
        invite = get_object_or_404(self.model_class.objects.filter(speaker_id=speaker_id), meetup_id=meetup_id)
        serializer = self.serializer_class(invite, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_id="delete_single_invite", operation_description="Отменить приглашение", tags=["Invites"])
    @method_permission_classes((IsUser, IsModerator))
    def delete(self, request, meetup_id, speaker_id, format=None):
        invite = get_object_or_404(self.model_class.objects.filter(speaker_id=speaker_id), meetup_id=meetup_id)
        invite.delete()
        return Response({"message":"Successfully deleted."})
    
class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser

    def create(self, request):
        if self.model_class.objects.filter(username=request.data.get('username', None)).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            self.model_class.objects.create_user(username=serializer.data['username'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserSerializer, tags=['Accounts'])
@api_view(['POST'])
@permission_classes([IsGuest])
def login_view(request):
    username =  request.data.get('username', False)
    password =  request.data.get('password', False)
    user = authenticate(username=username, password=password) if username and password else None
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, username)
        response = JsonResponse({'status': 'OK'}, status=200)
        response.set_cookie("session_id", random_key)
        return response
    else:
        return JsonResponse({'status': 'error', 'error': 'Login failed'}, status=400)
    
@csrf_exempt
@swagger_auto_schema(method='post', tags=['Accounts'])
@api_view(['POST'])
@permission_classes([IsAuthentificated])
def logout_view(request):
    response = JsonResponse({'status': 'OK'}, status=200)
    session_id = request.COOKIES.get('session_id', None)
    session_storage.delete(session_id)
    response.delete_cookie('session_id')
    return response
        



