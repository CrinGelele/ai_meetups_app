from django.db import models
from django.conf import settings
from datetime import date

class Speaker(models.Model):
    first_name = models.CharField(max_length = 35, blank = False)
    last_name = models.CharField(max_length = 35, blank = False)
    workplace = models.CharField(max_length = 50, blank = False)
    description = models.TextField(null = True, blank = True)
    img_url = models.TextField(null = True, blank = True)
    deletion_flag = models.BooleanField(default = 0, blank = False)
    class Meta:
        db_table = "speakers"

class Meetup(models.Model):
    status = models.CharField(max_length = 15, blank = False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank = False, related_name="user_action")
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank = True, null = True, related_name="moderator_action")
    creation_date = models.DateTimeField(auto_now_add = True, blank = False)
    submit_date = models.DateTimeField(null = True, blank = True)
    resolve_date = models.DateTimeField(null = True, blank = True)
    topic = models.TextField(null = True, blank = True)
    meetup_date = models.DateTimeField(null = True, blank = True)
    class Meta:
        db_table = "meetups"

class Invite(models.Model):
    speaker = models.ForeignKey('Speaker', on_delete=models.PROTECT, blank = False)
    meetup = models.ForeignKey('Meetup', on_delete=models.PROTECT, blank = False)
    approx_perfomance_duration = models.IntegerField(null = True, blank = True)
    class Meta:
        db_table = "invites"
        constraints = [
            models.UniqueConstraint(fields=['speaker', 'meetup'], name='UQ_Invites_speaker_id_and_meetup_id')
        ]
