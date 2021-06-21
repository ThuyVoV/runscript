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

        # specific functions needs a minimum of certain permission
        try:
            user = args[0].user
            fun = self.func.__name__
            need_view = ["script_detail"]
            need_edit = ["script_change", "script_confirm_edit", "script_confirm_delete"]
            need_log = ["logs"]
            need_manage = ["manage_user"]

            if fun in need_view:
                if not user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_view"):
                    return redirect('runscript:view_and_upload', script_list.id)
            elif fun in need_edit:
                if not user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_edit"):
                    return redirect('runscript:view_and_upload', script_list.id)
            elif fun in need_log:
                if not user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_log"):
                    return redirect('runscript:view_and_upload', script_list.id)
            elif fun in need_manage:
                if not user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_manage_user"):
                    return redirect('runscript:view_and_upload', script_list.id)

        except AttributeError:
            print("function no name")

        return self.func(*args, **kwargs)

