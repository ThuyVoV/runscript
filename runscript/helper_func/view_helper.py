from django.conf import settings
from runscript.models import UploadFileModel


def get_paths(file_id):
    url = UploadFileModel.objects.get(pk=file_id).upload_file.url
    file_path = f'{settings.BASE_DIR}{url}'
    return url, file_path


def get_file_content(file_path):
    fc = []
    with open(file_path, 'r') as f:
        for line in f:
            fc.append(line)
    f.close()
    return fc


def get_temp():
    return f'{settings.BASE_DIR}/runscript/scripts/temp.txt'


def write_to_file(content, file_path):
    with open(file_path, 'w') as f:
        for line in content:
            f.write(line)
    f.close()