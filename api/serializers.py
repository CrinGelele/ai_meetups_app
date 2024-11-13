from speakers.models import Speaker, Invite, Meetup, AuthUser
from rest_framework import serializers


class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ["id", "first_name", "last_name", "workplace", "description", "img_url"]

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

class InviteSerializer(serializers.ModelSerializer):
    meetup = serializers.CharField(read_only = True)
    speaker = serializers.CharField(read_only = True)
    class Meta:
        model = Invite
        fields = ["id", "meetup", "speaker", "approx_perfomance_duration"]

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ["id", "first_name", "last_name", "email"]