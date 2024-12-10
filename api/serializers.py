from speakers.models import Speaker, Invite, Meetup, CustomUser
from rest_framework import serializers
from collections import OrderedDict

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ["id", "first_name", "last_name", "workplace", "description", "img_url"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields

class MeetupSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', allow_null = True, read_only = True),
    moderator = serializers.CharField(source='moderator.username', allow_null = True, read_only = True)
    creation_date = serializers.CharField(read_only = True)
    submit_date = serializers.CharField(read_only = True)
    resolve_date = serializers.CharField(read_only = True)
    viewers = serializers.CharField(read_only = True)
    class Meta:
        model = Meetup
        fields = ["id", "status", "user", "moderator", "creation_date", "submit_date", "resolve_date", "topic", "meetup_date", "viewers"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields

class InviteSerializer(serializers.ModelSerializer):
    meetup = serializers.CharField(read_only = True)
    speaker = SpeakerSerializer(read_only=True)
    class Meta:
        model = Invite
        fields = ["id", "meetup", "speaker", "approx_perfomance_duration"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields
        
class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'is_staff', 'is_superuser']

'''
class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ["id", "first_name", "last_name", "email"]
        read_only_fields = ['id']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields

class AuthUserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ["username", "first_name", "last_name", "email", "username", "password"]
        write_only_fields = ['password']

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields

class AuthUserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)'''