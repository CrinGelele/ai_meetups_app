from django.shortcuts import render
import wget
import os
from django.http import HttpResponse

speakers = {
    1: {
       'name': 'Дмитрий',
       'surname': 'Ветров',
       'short_disc': 'Constructor University, Bremen',
       'long_disc': 'К.ф.-м.н., профессор компьютерных наук в Constructor University, Bremen, профессор компьютерных наук в Высшей Школе Экономики',
       'img_url': 'http://localhost:9000/speakers-img-storage/dmitry_vetrov.jpg'
    },
    2: {
       'name': 'Михаил',
       'surname': 'Бурцев',
       'short_disc': 'London Institute for Mathematical Sciences',
       'long_disc': 'Является стипендиантом им. Ландау в Лондонском Институте Математических Наук. Ранее был научным руководителем Научно-исследовательского института Искусственного Интеллекта, а также руководителем лаборатории нейронных сетей и глубокого обучения МФТИ. Под его руководством была разработана платформа диалогового искусственного интеллекта DeepPavlov.',
       'img_url': 'http://localhost:9000/speakers-img-storage/mikhail_burtsev.jpg'
    },
    3: {
       'name': 'Константин',
       'surname': 'Анохин',
       'short_disc': 'Moscow State University',
       'long_disc': 'Академик РАН, руководитель научно-образовательной школы «Мозг, когнитивные системы, искусственный интеллект», директор Института перспективных исследований мозга МГУ имени М.В.Ломоносова, заведующий лабораторией нейробиологии памяти НИИ нормальной физиологии имени П.К.Анохина.',
       'img_url': 'http://localhost:9000/speakers-img-storage/konstantin_anokhin.jpg'
    }
}

meetups = {
    1: {
        'date': '2024-10-03',
        'topic': 'AI',
    }
}

meetups_speakers = {
    1: {
        'meetup_id': 1,
        'speaker_id': 1,
    },
    2: {
        'meetup_id': 1,
        'speaker_id': 3,
    }
}

current_meetup_id = 1

def speakers_menu(request):
    srch = request.GET.get('srch')
    speakers_quantity = 0
    speakers_to_go = {}
    for value in meetups_speakers.values():
        if value['meetup_id'] == current_meetup_id:
            speakers_quantity += 1
    if not srch:
        speakers_to_go = speakers
    else:
        for key, value in speakers.items():
            if srch in value['name'] or srch in value['surname']:
                speakers_to_go[key] = value
    context = {'speakers': speakers_to_go, 'current_meetup_id': current_meetup_id, 'meetup': meetups[current_meetup_id],
               'speakers_quantity': speakers_quantity, 'srch': '' if not srch else srch}
    return render(request, 'speakers/speaker_cards.html', context)

def speaker_page(request):
    speaker_id = int(request.GET.get('speaker_id'))
    context = {'speaker_info': speakers[speaker_id]}
    return render(request, 'speakers/speaker_page.html', context)

def meetup_page(request):
    meetup_id = int(request.GET.get('meetup_id'))
    speakers_list = {}
    for key, value in meetups_speakers.items():
        if value['meetup_id'] == meetup_id:
            speakers_list[key] = speakers[value['speaker_id']]
    context = {'meetup_id': meetup_id, 'meetup_info': meetups[meetup_id], 'speakers_list': speakers_list}
    return render(request, 'speakers/meetup_page.html', context)