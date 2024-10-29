from django.db import models

class Speaker(models.Model):
    first_name = models.CharField(max_length=35, blank=False)
    last_name = models.CharField(max_length=35, blank=False)
    workplace = models.CharField(max_length=50, blank=False)
    description = models.TextField()
    img_url = models.TextField()
    deletion_flag = models.BooleanField(default=0, blank = False)
    class Meta:
        db_table = "speakers"

'''class Meetup(models.Model):
    class Meta:
        db_table = "meetups"

class Invite(models.Model):
    speaker = models.ForeignKey('Speaker', on_delete=models.PROTECT)
    meetup = models.ForeignKey('Meetup', on_delete=models.PROTECT)
    approx_perfomance_duration = models.IntegerField(blank = False)
    class Meta:
        db_table = "invites"
        constraints = [
            models.UniqueConstraint(fields=['speaker', 'meetup'], name='UQ_Invites_speaker_id_and_meetup_id')
        ]
'''