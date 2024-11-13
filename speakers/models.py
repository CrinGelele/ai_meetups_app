from django.db import models
from django.conf import settings
from datetime import date
from random import randint

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
    user = models.ForeignKey('AuthUser', on_delete=models.PROTECT, blank = False, related_name="user_action")
    moderator = models.ForeignKey('AuthUser', on_delete=models.PROTECT, blank = True, null = True, related_name="moderator_action")
    creation_date = models.DateTimeField(auto_now_add = True, blank = False)
    submit_date = models.DateTimeField(null = True, blank = True)
    resolve_date = models.DateTimeField(null = True, blank = True)
    topic = models.TextField(null = True, blank = True)
    meetup_date = models.DateTimeField(null = True, blank = True)
    viewers = models.IntegerField(null = True, blank = True)

    def save(self, force_insert=False, force_update=False):
        if self.status == 'Завершён':
            self.viewers = randint(1, 50)
        super(Meetup, self).save(force_insert, force_update)

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

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'
