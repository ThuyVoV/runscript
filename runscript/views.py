from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView

from .models import UploadFileModel, ScriptList
from .forms import UploadFileForm, CreateScriptListForm

from runscript.helper_func.decorators import AccessCheck
from .helper_func import view_helper as vh

import subprocess
import sys
import os
import shlex


# create an empty lists that will hold scripts
@login_required(login_url='/login/')
@AccessCheck
def create_list(request):
    perm_attributes = [
        'view', 'add', 'edit', 'run', 'delete',
        'log', 'manage_user', 'manage_perm'
    ]
    context = {
        'allLists': request.user.user_script_list.all(),
        'my_list': ScriptList.objects.filter(owner=str(request.user)),
        'form': CreateScriptListForm()
    }

    if request.method == "POST":
        if request.POST.get("create"):
            form = CreateScriptListForm(request.POST)
            if form.is_valid():
                # grab the string from the input and create the list with that name
                # then saving that list to a specific user
                ln = form.cleaned_data["list_name"]
                sl = ScriptList(list_name=ln, owner=request.user)

                # create lists of permissions for this new script list
                for p in perm_attributes:
                    Permission.objects.get_or_create(
                        codename=f"{request.user}_{ln}_can_{p}",
                        name=f"{request.user} {ln} can {p}",
                        content_type=ContentType.objects.get_for_model(UploadFileModel),
                    )
                    perm = Permission.objects.get(codename=f"{request.user}_{ln}_can_{p}")
                    request.user.user_permissions.add(perm)

                sl.save()
                request.user.user_script_list.add(sl)
                context['form'] = form

        elif request.POST.get("button_del_list"):
            if request.POST.get("list_del") == "Delete List":
                pass
            else:
                list_name = request.POST.get("list_del").split(' ')[-1]
                script_list = ScriptList.objects.get(list_name=list_name)

                if str(request.user) == script_list.owner:
                    for p in perm_attributes:
                        Permission.objects.get(codename=f"{script_list.owner}_{script_list.list_name}_can_{p}").delete()

                    script_list.delete()

    return render(request, 'runscript/create_list.html', context)


@login_required(login_url='/login/')
@AccessCheck
def view_and_upload(request, list_id):
    script_list = ScriptList.objects.get(pk=list_id)

    context = {
        'script_list': script_list,
    }

    vh.get_perms(request, script_list, context)

    form = UploadFileForm()
    if request.method == 'POST':
        if request.POST.get("button_upload"):
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                # add a file to the specific list with the list_id and save it
                new_script = form.cleaned_data["script_name"]
                new_file = form.cleaned_data["upload_file"]
                script_list.uploadfilemodel_set.create(script_name=new_script, upload_file=new_file)
                script_log = f'{request.user} uploaded {new_script} to {script_list.list_name}'
                script_list.scriptlog_set.create(action=script_log, person=request.user)

                return redirect('runscript:view_and_upload', list_id)

    context['form'] = form

    return render(request, 'runscript/view_and_upload.html', context)


@login_required(login_url='/login/')
@AccessCheck
def manage_user(request, list_id):
    script_list = ScriptList.objects.get(pk=list_id)
    context = {
        'script_list': script_list,
    }
    vh.get_perms(request, script_list, context)

    perm_attributes = [
        'view', 'add', 'edit', 'run', 'delete',
        'log', 'manage_user', 'manage_perm'
    ]
    if request.method == 'POST':
        # ADD USER
        if request.POST.get("button_add_user"):
            add_user = request.POST.get('add_user_to_list')
            # only owner of list can add to users
            if str(request.user) == script_list.owner:
                if User.objects.filter(username=add_user).exists():
                    messages.success(request, f'You added {add_user} to {script_list.list_name}')
                    script_list.user.add(User.objects.get(username=add_user).pk)

                    perm = Permission.objects.get(codename=f"{script_list.owner}_{script_list.list_name}_can_view")
                    User.objects.get(username=add_user).user_permissions.add(perm)

                    script_log = f'{request.user} added {add_user} to {script_list.list_name}'
                    script_list.scriptlog_set.create(action=script_log, person=request.user)
                else:
                    messages.error(request, "User does not exist.")
            else:
                messages.error(request, "you must be the owner of this list")

        # DELETE USER
        elif request.POST.get("button_del_user"):
            if request.POST.get('selected_user') == "Select User":
                messages.info(request, "No changes were made")
                return render(request, 'runscript/manage_user.html', context)

            del_user = request.POST.get('selected_user')

            if str(request.user) == script_list.owner:
                if User.objects.filter(username=del_user).exists():
                    messages.success(request, f'You deleted {del_user} from {script_list.list_name}')
                    script_list.user.remove(User.objects.get(username=del_user).pk)
                    script_log = f'{request.user} deleted {del_user} from {script_list.list_name}'
                    script_list.scriptlog_set.create(action=script_log, person=request.user)
                else:
                    messages.error(request, "That user does not exist.")
            else:
                messages.error(request, "you must be the owner of this list")

        # CHANGE USER PERMISSION
        elif request.POST.get("button_change_perm"):

            if request.POST.get('selected_user') == "Select User":
                messages.info(request, "No changes were made")
                return render(request, 'runscript/manage_user.html', context)

            user = User.objects.get(username=request.POST.get("selected_user"))

            for p in perm_attributes:
                perm = Permission.objects.get(codename=f"{script_list.owner}_{script_list.list_name}_can_{p}")
                if request.POST.get(p) == "clicked":
                    user.user_permissions.add(perm)
                    messages.info(request, f"Gave {user} {p} permission")
                else:
                    if p == "manage_perm" or p == "manage_user":
                        if user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_{p}") \
                                and str(request.user) != script_list.owner:
                            messages.warning(request, f"You cannot remove {p} permission from {user}")
                            return render(request, 'runscript/manage_user.html', context)
                    user.user_permissions.remove(perm)
                    messages.info(request, f"Remove {user} {p} permission")

        # USER SELECTION
        elif request.POST.get("button_select_user"):
            pass
            # if request.POST.get("selected_user") == "Select User":
            #     return render(request, 'runscript/manage_user.html', context)
            #
            # user = User.objects.get(username=request.POST.get("selected_user"))
            # has_perm = []
            # for p in perm_attributes:
            #     has_perm.append(user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_{p}"))
            #
            # # boolean to display the permissions once a user is selected
            # context['perm'] = zip(has_perm, perm_attributes)
            # context['selected_user'] = user

    if request.is_ajax():
        print("im in manage ajax")
        # if request.GET.get("selected_user") == "Select User":
        #     print('ok whatver')
        #     dad = ["hehe", 'ok', 'yay']
        #     #return render(request, 'runscript/manage_user.html', context)
        #     return JsonResponse({"data": dad})


        users=[]
        for u in script_list.user.all():
            users.append(str(u))
        context['script_list'] = {
            'user': users,
            'list_name': script_list.list_name,
            'owner': script_list.owner
        }

        user = User.objects.get(username=request.GET.get("selected_user"))
        has_perm = []
        for p in perm_attributes:
            has_perm.append(user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_{p}"))

        # boolean to display the permissions once a user is selected
        # context['perm'] = zip(has_perm, perm_attributes)
        # context['selected_user'] = user
        #context['has_perm'] = has_perm
        context['perm_attributes'] = perm_attributes


        return JsonResponse(context)

    return render(request, 'runscript/manage_user.html', context)


@login_required(login_url='/login/')
@AccessCheck
def script_detail(request, file_id):
    script_list = vh.get_list(file_id=file_id)
    output = []
    context = {
        'script_name': UploadFileModel.objects.get(pk=file_id),

    }

    vh.get_perms(request, script_list, context)

    # when they click run script, call the script with argument
    # write the output to a temp file to display it on screen, delete temp file
    if request.method == 'POST':
        if request.POST.get("button_run_script"):
            args = request.POST.get("arguments")
            t = open(vh.get_temp(), 'w')

            # get arguments separated by space and quotes example:
            # 123 "hello there" 456 -> ['123', 'hello there', 456']
            args = shlex.split(args)
            subprocess.run([sys.executable, context['script_name'].upload_file.path] + args, text=True, stdout=t)

            t.close()
            with open(vh.get_temp(), 'r') as t:
                for line in t:
                    output.append(line)
            t.close()

    context['fileContent'] = vh.get_file_content(context['script_name'].upload_file.path)
    context['output'] = output

    return render(request, 'runscript/script_detail.html', context)


@login_required(login_url='/login/')
@AccessCheck
def script_change(request, file_id):
    script_list = vh.get_list(file_id=file_id)
    context = {
        'script_name': UploadFileModel.objects.get(pk=file_id),
        'filename': UploadFileModel.objects.get(pk=file_id).upload_file.url.split('/')[-1],
        'fileContent': vh.get_file_content(UploadFileModel.objects.get(pk=file_id).upload_file.path),
    }

    vh.get_perms(request, script_list, context)

    # if pressing no on edit confirmation return back to change page
    # while keeping the edits
    if request.method == "POST":
        if request.POST.get("button_no"):
            context['fileContent'] = vh.get_file_content(vh.get_temp())
            return render(request, 'runscript/script_change.html', context)

    return render(request, 'runscript/script_change.html', context)


# after pressing edit button on change page
@login_required(login_url='/login/')
@AccessCheck
def script_confirm_edit(request, file_id):
    url, file_path = vh.get_paths(file_id)
    script_list = vh.get_list(file_id=file_id)
    context = {
        'url': url,
        'script_name': UploadFileModel.objects.get(pk=file_id),
        'filename': url.split('/')[-1],
    }
    vh.get_perms(request, script_list, context)

    script_list = ScriptList.objects.get(pk=context['script_name'].script_list_id)
    if request.method == 'POST':
        if request.POST.get("button_edit"):
            vh.write_to_file(request.POST.get('script_edit'), vh.get_temp())
            context['fileContent'] = vh.get_file_content(vh.get_temp())

            return render(request, 'runscript/script_confirm_edit.html', context)

        if request.POST.get("button_edit_yes"):
            url, file_path = vh.get_paths(file_id)
            temp = open(vh.get_temp(), 'r')
            vh.write_to_file(temp, file_path)
            temp.close()
            script_log = f"{request.user} edited {context['script_name']}"
            script_list.scriptlog_set.create(action=script_log, person=request.user)

            return redirect("runscript:detail", file_id)

    return render(request, 'runscript/script_confirm_edit.html', context)


# after pressing delete button on change page
@login_required(login_url='/login/')
@AccessCheck
def script_confirm_delete(request, file_id):
    url, file_path = vh.get_paths(file_id)
    script_list = vh.get_list(file_id=file_id)
    context = {
        'url': url,
        'script_name': UploadFileModel.objects.get(pk=file_id),
        'filename': url.split('/')[-1],
        'fileContent': vh.get_file_content(file_path),
    }
    vh.get_perms(request, script_list, context)

    script_list = ScriptList.objects.get(pk=context['script_name'].script_list_id)

    if request.method == "POST":
        if request.POST.get("button_delete_yes"):
            os.remove(file_path)
            UploadFileModel.objects.get(pk=file_id).delete()
            script_log = f"{request.user} deleted {context['script_name']}"
            script_list.scriptlog_set.create(action=script_log, person=request.user)
            return redirect('runscript:view_and_upload', context['script_name'].script_list_id)

    return render(request, 'runscript/script_confirm_delete.html', context)


# changed page_obj to logs for pagination
@login_required(login_url='/login/')
@AccessCheck
def logs(request, list_id):
    script_list = ScriptList.objects.get(pk=list_id)

    context = {
        'logs': script_list.scriptlog_set.all()[::-1],
        'pk': list_id,
        'is_paginated': True
    }

    vh.get_perms(request, script_list, context)

    display_amt = 10
    paginator = Paginator(context['logs'], display_amt)
    page_num = request.GET.get("page")

    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    context['logs'] = page

    return render(request, 'runscript/logs.html', context)


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(AccessCheck, name='dispatch')
class Logs(ListView):
    model = ScriptList
    context_object_name = 'logs'
    template_name = 'runscript/logs.html'
    paginate_by = 5

    def get_queryset(self):
        script_log = ScriptList.objects.get(pk=self.kwargs['pk']).scriptlog_set.all()[::-1]
        return script_log

    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # get all the scriptLog (from get_queryset)
        context = super().get_context_data(**kwargs)
        paginator = Paginator(context['logs'], self.paginate_by)
        page_num = self.request.GET.get("page")

        try:
            page = paginator.page(page_num)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        context['logs'] = page
        context['pk'] = self.kwargs['pk']

        script_list = vh.get_list(list_id=self.kwargs['pk'])
        user = self.request.user
        context['can_log'] = user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_log")

        return context


def ajax_test(request):
    perm_attributes = [
        'view', 'add', 'edit', 'run', 'delete',
        'log', 'manage_user', 'manage_perm'
    ]

    print(request.GET.get("forreal"))
    print(request.GET.get("nextnext"))

    if request.is_ajax():
        print("VERY COOL THIS IS AJAX")
        print("this user was selected:", request.GET.get("selected"))

    return JsonResponse({'notuser': perm_attributes})
