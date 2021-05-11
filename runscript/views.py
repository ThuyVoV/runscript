from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
from django.views.generic.list import ListView

from .models import UploadFileModel, ScriptList
from .forms import UploadFileForm, CreateScriptListForm

from runscript.helper_func.decorators import access_check
from .helper_func import view_helper as vh

import subprocess
import sys
import os
import shlex


# create an empty lists that will hold scripts
@login_required(login_url='/login/')
def create_list(request):

    if request.method == "POST":
        form = CreateScriptListForm(request.POST)
        if form.is_valid():
            # grab the string from the input and create the list with that name
            # then saving that list to a specific user
            ln = form.cleaned_data["list_name"]
            sl = ScriptList(list_name=ln, owner=request.user)
            sl.save()
            request.user.user_script_list.add(sl)

            # make group owner_groupname
    else:
        form = CreateScriptListForm()

    context = {
        'form': form,
        'allLists': request.user.user_script_list.all()
    }

    return render(request, 'runscript/create_list.html', context)


@login_required(login_url='/login/')
@access_check
def view_and_upload(request, list_id):
    script_list = ScriptList.objects.get(pk=list_id)

    context = {
        'script_list': script_list,
    }

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
        else:
            form = UploadFileForm()
    else:
        form = UploadFileForm()

    context['form'] = form

    return render(request, 'runscript/view_and_upload.html', context)


@login_required(login_url='/login/')
@access_check
def manage_user(request, list_id):
    script_list = ScriptList.objects.get(pk=list_id)

    if request.method == 'POST':
        if request.POST.get("button_add_user"):
            add_user = request.POST.get('add_user_to_list')

            # only owner of list can add to users
            if str(request.user) == script_list.owner:
                if User.objects.filter(username=add_user).exists():
                    messages.success(request, f'You added {add_user} to {script_list.list_name}')
                    script_list.user.add(User.objects.get(username=add_user).pk)
                    script_log = f'{request.user} added {add_user} to {script_list.list_name}'
                    script_list.scriptlog_set.create(action=script_log, person=request.user)

                    userx = User.objects.get(username=add_user)


                    # perm = Permission.objects.get(name='Can add upload file model')
                    #perm = Permission.objects.get(codename='upload file model')
                    # userx.user_permissions.remove(perm)
                    # userx.user_permissions.add(perm)
                    print(f'A {userx}')
                    # print(f'B {perm}')
                    print(f'C {userx.get_all_permissions()}')
                    print(f"D {userx.has_perm('runscript.can_upload_script')}")
                    print(f"E {userx.get_user_permissions()}")
                    #userx.perm
                else:
                    messages.error(request, "That user does not exist.")
            else:
                messages.error(request, "you must be the owner of this list")

        elif request.POST.get("button_del_user"):
            del_user = request.POST.get('del_user_from_list')

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

    return render(request, 'runscript/manage_user.html', {'script_list': script_list})


@login_required(login_url='/login/')
@access_check
def script_detail(request, file_id):
    output = []
    context = {
        'script_name': UploadFileModel.objects.get(pk=file_id),
    }

    # when they click run script, call the script with argument
    # write the output to a temp file to display it on screen, delete temp file
    if request.method == 'POST':
        if request.POST.get("button_run_script"):
            args = request.POST.get("arguments")
            t = open(vh.get_temp(), 'w')

            # get arguments separated by space and quotes
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
@access_check
def script_change(request, file_id):


    context = {
        'script_name': UploadFileModel.objects.get(pk=file_id),
        'filename': UploadFileModel.objects.get(pk=file_id).upload_file.url.split('/')[-1],
        'fileContent': vh.get_file_content(UploadFileModel.objects.get(pk=file_id).upload_file.path)
    }

    # if pressing no on edit confirmation return back to change page
    # while keeping the edits
    if request.method == "POST":
        if request.POST.get("button_no"):
            context['fileContent'] = vh.get_file_content(vh.get_temp())
            return render(request, 'runscript/script_change.html', context)

    return render(request, 'runscript/script_change.html', context)


# after pressing edit button on change page
@login_required(login_url='/login/')
@access_check
def script_confirm_edit(request, file_id):


    url, file_path = vh.get_paths(file_id)

    context = {
        'url': url,
        'script_name': UploadFileModel.objects.get(pk=file_id),
        'filename': url.split('/')[-1],
    }
    script_list = ScriptList.objects.get(pk=context['script_name'].script_list_id)
    if request.method == 'POST':
        if request.POST.get("button_edit"):
            print("making sure")
            vh.write_to_file(request.POST.get('script_edit'), vh.get_temp())
            context['fileContent'] = vh.get_file_content(vh.get_temp())

            return render(request, 'runscript/script_confirm_edit.html', context)

        if request.POST.get("button_edit_yes"):
            print("pressed edit yes")
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
@access_check
def script_confirm_delete(request, file_id):
    url, file_path = vh.get_paths(file_id)
    context = {
        'url': url,
        'script_name': UploadFileModel.objects.get(pk=file_id),
        'filename': url.split('/')[-1],
        'fileContent': vh.get_file_content(file_path)
    }

    script_list = ScriptList.objects.get(pk=context['script_name'].script_list_id)
    print(context['script_name'].script_list_id)
    if request.method == "POST":
        if request.POST.get("button_delete_yes"):
            os.remove(file_path)
            UploadFileModel.objects.get(pk=file_id).delete()
            script_log = f"{request.user} deleted {context['script_name']}"
            script_list.scriptlog_set.create(action=script_log, person=request.user)
            return redirect('runscript:view_and_upload', context['script_name'].script_list_id)

    return render(request, 'runscript/script_confirm_delete.html', context)


@login_required(login_url='/login/')
@access_check
def logs(request, list_id):
    script_list = ScriptList.objects.get(pk=list_id)

    users = []
    a = list(script_list.scriptlog_set.all()[::-1])
    for u in a:
        users.append(str(u).split(' ')[0])

    context = {
        'logs': zip(script_list.scriptlog_set.all()[::-1], users)
    }

    return render(request, 'runscript/logs.html', context)


class Logs(ListView):
    model = ScriptList
    context_object_name = 'logs'
    template_name = 'runscript/logs.html'
    paginate_by = 20

    def get_queryset(self):
        script_log = ScriptList.objects.get(pk=self.kwargs['pk']).scriptlog_set.all()[::-1]
        return script_log

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

        return context
