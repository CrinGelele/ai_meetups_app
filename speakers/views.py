from django.shortcuts import render
import wget
import os
from django.http import HttpResponse

speakers = {
    1: {
       'name': 'Дмитрий',
       'surname': 'Ветров',
       'short_disc': 'Бременский КУ',
       'long_disc': 'К.ф.-м.н., профессор компьютерных наук в Бременском Конструкторском Университете, профессор компьютерных наук в Высшей Школе Экономики',
       'img_url': 'http://localhost:9000/speakers-img-storage/dmitry_vetrov.jpg'
    },
    2: {
       'name': 'Михаил',
       'surname': 'Бурцев',
       'short_disc': 'Лондонский ИМН',
       'long_disc': 'Является стипендиантом им. Ландау в Лондонском Институте Математических Наук. Ранее был научным руководителем Научно-исследовательского института Искусственного Интеллекта, а также руководителем лаборатории нейронных сетей и глубокого обучения МФТИ. Под его руководством была разработана платформа диалогового искусственного интеллекта DeepPavlov.',
       'img_url': 'http://localhost:9000/speakers-img-storage/mikhail_burtsev.jpg'
    },
    3: {
       'name': 'Константин',
       'surname': 'Анохин',
       'short_disc': 'МГУ',
       'long_disc': 'Академик РАН, руководитель научно-образовательной школы «Мозг, когнитивные системы, искусственный интеллект», директор Института перспективных исследований мозга МГУ имени М.В.Ломоносова, заведующий лабораторией нейробиологии памяти НИИ нормальной физиологии имени П.К.Анохина.',
       'img_url': 'http://localhost:9000/speakers-img-storage/konstantin_anokhin.jpg'
    },
    4: {
       'name': 'Андрей',
       'surname': 'Капитонов',
       'short_disc': 'Рекламное агентство "Капитан", СПБ',
       'long_disc': 'Бесплатные лиды с Яндекс Карты.- Геолокация рулит. Яндекс Карты и Яндекс Бизнес. Как мы сделали ROMI 4300% по стоматологии. Ответы на вопросы.Социальные сети и мессенджерыО СПИКЕРЕАндрей Капитонов ⁃ Рекламное агентство «Капитан». Официальный партнер Яндекс.Бизнес. https://businessonmaps.pro – Спикер выставок «РИДО», «Реклама», «Мир детства», «ПетерФуд», “ProdExpo”. Конференциях «Суровый Питерский SMM», РБК «Предпринимательский класс 2.0», “Merge” и других. ⁃ Печатался в изданиях: Forbes, Российская газета, Деловой Петербург, Пресс-служба, Новинки рекламы, Аргументы и факты, Ведомости, Коммерсант, Мойка 78, Собесендник.ру, На Невском, Коммерческий директор, Своё дело плюс и т.д. ⁃ Телесюжеты: Первый канал, 78 канал, Телеканал 360, ТВ Санкт-Петербург, РазТВ, Россия-1, ТВ Мир.',
       'img_url': 'http://localhost:9000/speakers-img-storage/andrey_kapitonov.jpg'
    },
    5: {
       'name': 'Александр',
       'surname': 'Сенотов',
       'short_disc': 'Авито, Москва',
       'long_disc': 'Бывший юрист с 9-летним стажем; 6 лет в управлении IT продуктами: был продактом, лидом, CPO (МТС, Сбер, WASD.TV (http://wasd.tv/)); Создавал продукты в корпорации с нуля, растил команды, выгонял токсиков и сам создавал токсичные условия, выстраивал процессы дискавери, деливери, work-life balance, а еще — пищевое поведение своих котов; Развивал сервисы для создателей контента и геймеров. Был ментором для талантливых девушек в проекте Women in Tech.',
       'img_url': 'http://localhost:9000/speakers-img-storage/alexander_senotov.jpg'
    }
}

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
    speakers_to_go = {}
    for meetup in meetups:
        if meetup['id'] == current_meetup_id:
            current_meetup = meetup
            speakers_quantity = len(meetup['speakers'])
            break
    if not speaker_name_to_find:
        speakers_to_go = speakers
    else:
        for key, value in speakers.items():
            if speaker_name_to_find in value['name'] or speaker_name_to_find in value['surname']:
                speakers_to_go[key] = value
    context = {'speakers': speakers_to_go, 'current_meetup_id': current_meetup_id, 'meetup': current_meetup,
               'speakers_quantity': speakers_quantity, 'speaker_name_to_find': '' if not speaker_name_to_find else speaker_name_to_find}
    return render(request, 'speakers/speaker_cards.html', context)

def speaker_page(request, speaker_id):
    context = {'speaker_info': speakers[speaker_id]}
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