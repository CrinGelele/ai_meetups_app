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
       'img_url': 'http://192.168.1.80:35299/api/v1/download-shared-object/aHR0cDovLzEyNy4wLjAuMTo5MDAwL2FpbWEvZG1pdHJ5X3ZldHJvdi5qcGc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1YTVRHWVcxVDRPRlhEMExaQ1BZWSUyRjIwMjQxMDAyJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI0MTAwMlQwODM4MzZaJlgtQW16LUV4cGlyZXM9NDMyMDAmWC1BbXotU2VjdXJpdHktVG9rZW49ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmhZMk5sYzNOTFpYa2lPaUpZVFZSSFdWY3hWRFJQUmxoRU1FeGFRMUJaV1NJc0ltVjRjQ0k2TVRjeU56ZzVPVEV3T0N3aWNHRnlaVzUwSWpvaWJXbHVhVzloWkcxcGJpSjkuVHZ5bVdrZ0l6dmthZnJFZm9jZTRGTnlXeWsxSm9mTWMyeFhVanExdk53U2NnaUNKZ3QzVjBybzd1OTl5TW5xdUQzM1dZVXFhbkxFR2pwU1lKYnFmMXcmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JnZlcnNpb25JZD1udWxsJlgtQW16LVNpZ25hdHVyZT1lN2U3NWM1MjkxYzA1MWEwOWRlNDgzMGU5NGE5YzBjMTU5MzZlYmJiMGNiMTRkZDg2MzY5ZDBmMjdiYjhhNTg1',
       'img_short': 'img/dmitry_vetrov.jpg'
    },
    2: {
       'name': 'Михаил',
       'surname': 'Бурцев',
       'short_disc': 'London Institute for Mathematical Sciences',
       'long_disc': 'Является стипендиантом им. Ландау в Лондонском Институте Математических Наук. Ранее был научным руководителем Научно-исследовательского института Искусственного Интеллекта, а также руководителем лаборатории нейронных сетей и глубокого обучения МФТИ. Под его руководством была разработана платформа диалогового искусственного интеллекта DeepPavlov.',
       'img_url': 'http://192.168.1.80:35299/api/v1/download-shared-object/aHR0cDovLzEyNy4wLjAuMTo5MDAwL2FpbWEvbWlraGFpbF9idXJ0c2V2LmpwZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPVhNVEdZVzFUNE9GWEQwTFpDUFlZJTJGMjAyNDEwMDIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQxMDAyVDA4NTI0MVomWC1BbXotRXhwaXJlcz00MzE5OSZYLUFtei1TZWN1cml0eS1Ub2tlbj1leUpoYkdjaU9pSklVelV4TWlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaFkyTmxjM05MWlhraU9pSllUVlJIV1ZjeFZEUlBSbGhFTUV4YVExQlpXU0lzSW1WNGNDSTZNVGN5TnpnNU9URXdPQ3dpY0dGeVpXNTBJam9pYldsdWFXOWhaRzFwYmlKOS5UdnltV2tnSXp2a2FmckVmb2NlNEZOeVd5azFKb2ZNYzJ4WFVqcTF2TndTY2dpQ0pndDNWMHJvN3U5OXlNbnF1RDMzV1lVcWFuTEVHanBTWUpicWYxdyZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmdmVyc2lvbklkPW51bGwmWC1BbXotU2lnbmF0dXJlPWU2ZjAxNDI1NGE3YTJmZDg1N2NjZWJmOTIzMzQzOTI3OTk4NDYxMWJjMjg2MmQ2NjA0ZGI3ZGUwODJiMzAyMmE',
       'img_short': 'img/mikhail_burtsev.jpg'
    },
    3: {
       'name': 'Константин',
       'surname': 'Анохин',
       'short_disc': 'МГУ',
       'long_disc': 'Академик РАН, руководитель научно-образовательной школы «Мозг, когнитивные системы, искусственный интеллект», директор Института перспективных исследований мозга МГУ имени М.В.Ломоносова, заведующий лабораторией нейробиологии памяти НИИ нормальной физиологии имени П.К.Анохина.',
       'img_url': 'http://192.168.1.80:35299/api/v1/download-shared-object/aHR0cDovLzEyNy4wLjAuMTo5MDAwL2FpbWEva29uc3RhbnRpbl9hbm9raGluLmpwZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPVhNVEdZVzFUNE9GWEQwTFpDUFlZJTJGMjAyNDEwMDIlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQxMDAyVDA4NTMwNVomWC1BbXotRXhwaXJlcz00MzE5OSZYLUFtei1TZWN1cml0eS1Ub2tlbj1leUpoYkdjaU9pSklVelV4TWlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaFkyTmxjM05MWlhraU9pSllUVlJIV1ZjeFZEUlBSbGhFTUV4YVExQlpXU0lzSW1WNGNDSTZNVGN5TnpnNU9URXdPQ3dpY0dGeVpXNTBJam9pYldsdWFXOWhaRzFwYmlKOS5UdnltV2tnSXp2a2FmckVmb2NlNEZOeVd5azFKb2ZNYzJ4WFVqcTF2TndTY2dpQ0pndDNWMHJvN3U5OXlNbnF1RDMzV1lVcWFuTEVHanBTWUpicWYxdyZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmdmVyc2lvbklkPW51bGwmWC1BbXotU2lnbmF0dXJlPTljMGNiYWEzMTg0ZTMwZmM0NTQwNmE5NjEwMDE1NTUwM2VlOWQyZGMxMGRkNTE5ZGUyNGNhNzI2ZmEyNGFhNGQ',
       'img_short': 'img/konstantin_anokhin.jpg'
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

def get_media():
    for value in speakers.values():
        if os.path.exists('speakers/static/'+value['img_short']):
            os.remove('speakers/static/'+value['img_short']) # if exist, remove it directly
        wget.download(value['img_url'], 'speakers/static/'+value['img_short'])


def speakers_menu(request):
    get_media()
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