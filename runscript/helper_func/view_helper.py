from django.conf import settings
from runscript.models import UploadFileModel, ScriptList, TaskLog


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


def get_logs_dir():
    return f'{settings.BASE_DIR}/runscript/scripts/logs/'


def write_to_file(content, file_path):
    with open(file_path, 'w') as f:
        for line in content:
            f.write(line)
    f.close()


def get_list(**kwargs):
    if 'list_id' in kwargs:
        return ScriptList.objects.get(pk=int(kwargs['list_id']))
    elif 'file_id' in kwargs:
        script_list_id = UploadFileModel.objects.get(pk=int(kwargs['file_id'])).script_list_id
        return ScriptList.objects.get(pk=script_list_id)
    elif 'pk' in kwargs:
        return ScriptList.objects.get(pk=kwargs['pk'])
    elif 'output_id' in kwargs:
        script_list_id = TaskLog.objects.get(pk=int(kwargs['output_id'])).script_list_id
        return ScriptList.objects.get(pk=script_list_id)


def get_perms(request, script_list, context):
    check_perm = ['can_view', 'can_add', 'can_edit', 'can_run', 'can_delete', 'can_log', 'can_manage_user',
                  'can_manage_perm']
    for c in check_perm:
        context[c] = request.user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_{c}")


def get_perm_attr():
    return ['view', 'add', 'edit', 'run', 'delete', 'log', 'manage_user', 'manage_perm']


def arg_parse():
    return '```'
