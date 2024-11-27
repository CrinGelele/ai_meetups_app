from django.conf import settings
from rest_framework.response import Response
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('speakers-img-storage', image_name, file_object, file_object.size)
        return f"http://localhost:9000/speakers-img-storage/{image_name}"
    except Exception as e:
        return {"error": str(e)}

def process_file_remove(image_name):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            secure=settings.MINIO_USE_SSL
    )
    try:
        client.remove_object('speakers-img-storage', image_name)
        print('polu4ilos')
        return Response({"message": "success"})
    except Exception as e:
        return {"error": str(e)}


def add_pic(speaker, pic):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            secure=settings.MINIO_USE_SSL
    )
    img_obj_name = str(pic)
    if not pic:
        return Response({"error": "Нет файла."})
    result = process_file_upload(pic, client, img_obj_name)
    if 'error' in result:
        return Response(result)
    speaker.img_url = result
    speaker.save()
    return Response({"message": "success"})