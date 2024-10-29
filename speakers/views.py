from django.shortcuts import render
import wget
import os
from django.http import HttpResponse
from .models import Speaker

meetups = [
    {
        'id': 1,
        'date': '2024-10-03',
        'topic': 'AI',
        'speakers': [{'id': 1, 'approx_perfomance_duration': 30}, {'id': 3, 'approx_perfomance_duration': 45}]
    }
]

current_meetup_id = 1

def speakers_menu(request):
    speaker_name_to_find = request.GET.get('speaker_name_to_find')
    speakers_quantity = 0
    for meetup in meetups:
        if meetup['id'] == current_meetup_id:
            current_meetup = meetup
            speakers_quantity = len(meetup['speakers'])
            break
    context = {'speakers': Speaker.objects.all() if not speaker_name_to_find else Speaker.objects.filter(first_name__icontains = speaker_name_to_find) | Speaker.objects.filter(last_name__icontains = speaker_name_to_find),
                'current_meetup_id': current_meetup_id, 'meetup': current_meetup,
               'speakers_quantity': speakers_quantity, 'speaker_name_to_find': '' if not speaker_name_to_find else speaker_name_to_find}
    return render(request, 'speakers/speaker_cards.html', context)

def speaker_page(request, speaker_id):
    context = {'speaker_info': Speaker.objects.get(id=speaker_id)}
    return render(request, 'speakers/speaker_page.html', context)

def meetup_page(request, meetup_id):
    speakers_list = {}
    for meetup in meetups:
        if meetup['id'] == meetup_id:
            current_meetup = meetup
            for speaker in meetup['speakers']:
                speakers_list[speaker['id']] = {'speaker': speakers[speaker['id']],
                                                'approx_perfomance_duration': speaker['approx_perfomance_duration']}
            break
    context = {'meetup_id': meetup_id, 'meetup_info': current_meetup, 'speakers_list': speakers_list}
    return render(request, 'speakers/meetup_page.html', context)