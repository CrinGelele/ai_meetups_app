from django.contrib import admin
from .models import Speaker, Meetup, Invite, CustomUser

admin.site.register(Speaker)
admin.site.register(Meetup)
admin.site.register(Invite)
admin.site.register(CustomUser)
