from django.shortcuts import render, redirect
from .models import Speaker, Meetup, Invite
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import Q

current_user_id = 1

def invite_speaker(request):
    current_meetup = Meetup.objects.filter(user_id = current_user_id) &  Meetup.objects.filter(status = 'Черновик')
    current_meetup_id = current_meetup[0].id if current_meetup else None
    if request.method == 'POST':
        if current_meetup:
            Invite(meetup = Meetup.objects.get(id = current_meetup_id), speaker = Speaker.objects.get(id = request.POST['speaker_id'])).save()
        else:
            Meetup(status = 'Черновик', user = get_user_model().objects.get(id = current_user_id)).save()
            current_meetup = Meetup.objects.filter(user_id = current_user_id) &  Meetup.objects.filter(status = 'Черновик')
            current_meetup_id = current_meetup[0].id if current_meetup else None
            Invite(meetup = Meetup.objects.get(id = current_meetup_id), speaker = Speaker.objects.get(id = request.POST['speaker_id'])).save()
    return redirect(speakers_menu)

def delete_meetup(request):
    if request.method == 'POST':
        connection.cursor().execute("UPDATE meetups SET status = 'Удалена' WHERE id = %s", [request.POST['meetup_id']])
    return redirect(speakers_menu) 

def speakers_menu(request):
    current_meetup = Meetup.objects.filter(user_id = current_user_id) &  Meetup.objects.filter(status = 'Черновик')
    current_meetup_id = current_meetup[0].id if current_meetup else None
    speaker_name_to_find = request.GET.get('speaker_name_to_find')
    context = {'speakers': Speaker.objects.filter(~Q(deletion_flag = True)) if not speaker_name_to_find else Speaker.objects.filter(~Q(deletion_flag = True)) & (Speaker.objects.filter(first_name__icontains = speaker_name_to_find) | Speaker.objects.filter(last_name__icontains = speaker_name_to_find)),
                'current_meetup_id': current_meetup_id, 'meetup': Meetup.objects.get(id=current_meetup_id) if current_meetup_id else None,
               'speakers_quantity': len(Invite.objects.filter(meetup = current_meetup_id)) if current_meetup_id else None,
               'speaker_name_to_find': '' if not speaker_name_to_find else speaker_name_to_find} #if current_meetup_id else { 'meetup_deleted': True}
    return render(request, 'speakers/speaker_cards.html', context)

def speaker_page(request, speaker_id): 
    context = {'speaker_info': Speaker.objects.get(id=speaker_id)}
    return render(request, 'speakers/speaker_page.html', context)

def meetup_page(request, meetup_id):
    current_meetup = Meetup.objects.filter(id = meetup_id) & Meetup.objects.filter(~Q(status = 'Удалена'))
    current_meetup_id = current_meetup[0].id if current_meetup else None
    context = {'meetup_id': meetup_id, 'meetup_info': current_meetup[0] if current_meetup else None, 'invites': Invite.objects.filter(meetup = current_meetup_id)}
    return render(request, 'speakers/meetup_page.html', context)