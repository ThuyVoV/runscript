from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from runscript.models import UploadFileModel, ScriptList


# if the user is not in the list of user allowed, redirect to their main page
def access_check(func):
    def wrapper(request, *args, **kwargs):
        script_list = get_list(**kwargs)

        if request.user not in script_list.user.all():
            return redirect('runscript:main')

        return func(request, *args, **kwargs)
    return wrapper


def permission_check(func):
    def wrapper(request, *args, **kwargs):
        script_list = get_list(**kwargs)

        if request.user not in script_list.user.all():
            return redirect('runscript:main')

        return func(request, *args, **kwargs)
    return wrapper


def get_list(**kwargs):
    if 'list_id' in kwargs:
        return ScriptList.objects.get(pk=int(kwargs['list_id']))
    if 'file_id' in kwargs:
        script_list_id = UploadFileModel.objects.get(pk=int(kwargs['file_id'])).script_list_id
        return ScriptList.objects.get(pk=script_list_id)