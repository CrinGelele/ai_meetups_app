from django.db import models

class Speaker(models.Model):
    id = models.Field(primary_key = True)
    first_name = models.CharField(max_length=35, blank=False)
    last_name = models.CharField(max_length=35, blank=False)
    workplace = models.CharField(max_length=50, blank=False)
    description = models.TextField()
    img_url = models.TextField()
    deletion_flag = models.BooleanField(default=0, blank = False)
    class Meta:
        db_table = "speakers"

class Meetup(models.Model):
    id = models.Field(primary_key = True)
    class Meta:
        db_table = "meetups"

class Invite(models.Model):
    id = models.Field(primary_key = True)
    class Meta:
        db_table = "invites"