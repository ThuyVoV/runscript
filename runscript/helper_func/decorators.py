from django.shortcuts import redirect
from .view_helper import get_list


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