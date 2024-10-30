from django.contrib import admin
from .models import Speaker, Meetup, Invite

admin.site.register(Speaker)
admin.site.register(Meetup)
admin.site.register(Invite)
