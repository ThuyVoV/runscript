from django.shortcuts import redirect
from .view_helper import get_list


# if the user is not in the list of user allowed, redirect to their main page
# replaced by class AccessCheck
def access_check(func):
    def wrapper(request, *args, **kwargs):
        script_list = get_list(**kwargs)
        if request.user not in script_list.user.all():
            return redirect('runscript:main')

        return func(request, *args, **kwargs)
    return wrapper


class AccessCheck(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        script_list = get_list(**kwargs)
        if script_list is None:
            return self.func(*args, **kwargs)
        if args[0].user not in script_list.user.all():
            return redirect('runscript:main')
        return self.func(*args, **kwargs)


def permission_check(func):
    def wrapper(request, *args, **kwargs):
        script_list = get_list(**kwargs)

        if request.user not in script_list.user.all():
            return redirect('runscript:main')

        return func(request, *args, **kwargs)
    return wrapper
