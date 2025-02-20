import segno
import base64
from io import BytesIO

def generate_qr(meetup):
    # Формируем информацию для QR-кода
    info = f"Митап {meetup.meetup_date}\nПо теме{meetup.topic}\n\n"

    # Генерация QR-кода
    qr = segno.make(info)
    buffer = BytesIO()
    qr.save(buffer, kind='png')
    buffer.seek(0)

    # Конвертация изображения в base64
    qr_image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return qr_image_base64