# from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic.list import ListView

from .forms import UploadFileForm, CreateScriptListForm
from .models import FileTask, ScriptList, TaskLog, UploadFileModel
from .scheduler import scheduler

from .helper_func.decorators import AccessCheck
from .helper_func import view_helper as vh
from .helper_func import run_task as rt

import datetime
import os
import shlex
import subprocess
import sys


# create an empty lists that will hold scripts
@login_required(login_url='/login/')
@AccessCheck
def create_list(request):
    perm_attributes = vh.get_perm_attr()

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
    request.session['log_session'] = "search_task"
    request.session['log_search_session'] = ''

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
                current_time = datetime.datetime.now().strftime('%a %b %d, %Y %I:%M:%S %p')
                script_list.scriptlog_set.create(action=script_log, person=request.user, date_added=current_time)

                return redirect('runscript:view_and_upload', list_id)
            else:
                context['dupe'] = "That script name already exists, script names must be unique"

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

    perm_attributes = vh.get_perm_attr()

    if request.method == 'POST':
        # ADD USER
        if request.POST.get("button_add_user"):
            add_user = request.POST.get('add_user_to_list')
            # only owner of list can add to users
            if str(request.user) == script_list.owner:
                if User.objects.filter(username=add_user).exists():
                    # messages.success(request, f'You added {add_user} to {script_list.list_name}')
                    script_list.user.add(User.objects.get(username=add_user).pk)

                    perm = Permission.objects.get(codename=f"{script_list.owner}_{script_list.list_name}_can_view")
                    User.objects.get(username=add_user).user_permissions.add(perm)

                    script_log = f'{request.user} added {add_user} to {script_list.list_name}'
                    current_time = datetime.datetime.now().strftime('%a %b %d, %Y %I:%M:%S %p')
                    script_list.scriptlog_set.create(action=script_log, person=request.user, date_added=current_time)
                else:
                    pass
                    # messages.error(request, "User does not exist.")
            else:
                pass
                # messages.error(request, "you must be the owner of this list")

        # DELETE USER
        elif request.POST.get("button_del_user"):
            if request.POST.get('selected_user') == "Select User":
                # messages.info(request, "No changes were made")
                return render(request, 'runscript/manage_user.html', context)

            del_user = request.POST.get('selected_user')

            if str(request.user) == script_list.owner:
                if User.objects.filter(username=del_user).exists():
                    # messages.success(request, f'You deleted {del_user} from {script_list.list_name}')
                    script_list.user.remove(User.objects.get(username=del_user).pk)
                    script_log = f'{request.user} deleted {del_user} from {script_list.list_name}'
                    current_time = datetime.datetime.now().strftime('%a %b %d, %Y %I:%M:%S %p')
                    script_list.scriptlog_set.create(action=script_log, person=request.user, date_added=current_time)
                else:
                    pass
                    # messages.error(request, "That user does not exist.")
            else:
                pass
                # messages.error(request, "you must be the owner of this list")

        # CHANGE USER PERMISSION
        elif request.POST.get("button_change_perm"):

            if request.POST.get('selected_user') == "Select User":
                # messages.info(request, "No changes were made")
                return render(request, 'runscript/manage_user.html', context)

            user = User.objects.get(username=request.POST.get("selected_user"))

            for p in perm_attributes:
                perm = Permission.objects.get(codename=f"{script_list.owner}_{script_list.list_name}_can_{p}")
                if request.POST.get(p) == "clicked":
                    user.user_permissions.add(perm)
                    # messages.info(request, f"Gave {user} {p} permission")
                else:
                    if p == "manage_perm" or p == "manage_user":
                        if user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_{p}") \
                                and str(request.user) != script_list.owner:
                            # messages.warning(request, f"You cannot remove {p} permission from {user}")
                            return render(request, 'runscript/manage_user.html', context)
                    user.user_permissions.remove(perm)
                    # messages.info(request, f"Remove {user} {p} permission")

        # USER SELECTION
        elif request.POST.get("button_select_user"):

            if request.POST.get("selected_user") == "Select User":
                return render(request, 'runscript/manage_user.html', context)

            user = User.objects.get(username=request.POST.get("selected_user"))
            has_perm = []
            for p in perm_attributes:
                has_perm.append(user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_{p}"))

            # boolean to display the permissions once a user is selected
            context['perm'] = zip(has_perm, perm_attributes)
            context['selected_user'] = user

    if request.is_ajax():
        print("ajax requests")
        # AJAX SELECT USER
        if request.GET.get("pressed") == 'select':
            print("select clicked", request.GET.get("pressed"))

            users = []
            for u in script_list.user.all():
                users.append(str(u))
            context['script_list'] = {
                'user': users,
                'list_name': script_list.list_name,
                'owner': script_list.owner
            }

            user = User.objects.get(username=request.GET.get("selected_user"))
            check_perm = []
            for p in perm_attributes:
                check_perm.append(user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_{p}"))

            context['perm_attributes'] = perm_attributes

            # for p in perm_attributes:
            #     check_perm.append(context[f'can_{p}'])
            context['check_perm'] = check_perm

            return JsonResponse(context)

        # AJAX CHANGE USER PERMISSIONS
        if request.POST.get('pressed') == 'perm':
            print("perm clicked", request.POST.get('pressed'))
            # print("user selected", request.POST.get("selected_user"))
            context['script_list'] = "hah"

            user = User.objects.get(username=request.POST.get("selected_user"))
            # print("user type", type(user), "username", user)

            perm_list = request.POST.getlist('perm_list[]')
            # print("permlist", perm_list)
            message = []
            for b, p in zip(perm_list, perm_attributes):
                perm = Permission.objects.get(codename=f"{script_list.owner}_{script_list.list_name}_can_{p}")
                print(perm)
                if b == 'true':
                    if p == "manage_perm" or p == "manage_user":
                        if str(request.user) == script_list.owner:
                            user.user_permissions.add(perm)
                            # messages.info(request, f"Gave {user} {p} permission")
                            message.append(f"Gave {user} {p} permission")
                        else:
                            print("you must be owner")
                            message.append(f"Cannot give {user} {p} permission")
                    else:
                        user.user_permissions.add(perm)
                        message.append(f"Gave {user} {p} permission")

                else:
                    if p == "manage_perm" or p == "manage_user":
                        if user.has_perm(f"runscript.{script_list.owner}_{script_list.list_name}_can_{p}") \
                                and str(request.user) != script_list.owner:
                            # messages.warning(request, f"Cannot remove {p} permission from {user}")
                            continue

                    user.user_permissions.remove(perm)
                    # messages.info(request, f"Remove {user} {p} permission")
                    message.append(f"Remove {user} {p} permission")

            script_log = ""
            for m in message:
                script_log += m + "\n"

            current_time = datetime.datetime.now().strftime('%a %b %d, %Y %I:%M:%S %p')
            script_list.scriptlog_set.create(person=request.user, action=script_log, date_added=current_time)
            # print(script_log)

            context['message'] = message
            return JsonResponse(context)

        # AJAX DELETE USER
        if request.POST.get('pressed') == 'delete':
            print("del clicked", request.POST.get('pressed'))
            print("user selected", request.POST.get("selected_user"))
            context['script_list'] = "hah"
            del_user = request.POST.get("selected_user")

            if str(request.user) == script_list.owner:

                if User.objects.filter(username=del_user).exists():
                    # messages.success(request, f'You deleted {del_user} from {script_list.list_name}')
                    script_list.user.remove(User.objects.get(username=del_user).pk)
                    script_log = f'{request.user} deleted {del_user} from {script_list.list_name}'
                    current_time = datetime.datetime.now().strftime('%a %b %d, %Y %I:%M:%S %p')
                    script_list.scriptlog_set.create(action=script_log, person=request.user, date_added=current_time)
                    context['message'] = f"you delete {del_user}"
                    print("you delete")
            else:
                print("cannot delete")
                context['message'] = f"you cannot delete {del_user}"

            users = []
            for u in script_list.user.all():
                print(u)
                if str(u) == script_list.owner or str(u) == str(request.user):
                    continue
                users.append((str(u)))

            context['users'] = users

            return JsonResponse(context)

    return render(request, 'runscript/manage_user.html', context)


@login_required(login_url='/login/')
@AccessCheck
def script_detail(request, file_id):
    script_list = vh.get_list(file_id=file_id)
    output_text = []
    context = {
        'file': UploadFileModel.objects.get(pk=file_id),
    }

    vh.get_perms(request, script_list, context)
    context['task_scheduler'] = [
        "task_year", "task_month", "task_day",
        "task_week", "task_day_of_week",
        "task_hour", "task_minute", "task_second"
    ]

    # when they click run script, call the script with argument
    # write the output to a temp file to display it on screen, delete temp file
    if request.method == 'POST':
        args = request.POST.get("arguments")

        # get arguments separated by space and quotes example:
        # 123 "hello there" 456 -> ['123', 'hello there', 456']
        arguments = shlex.split(args)
        script_path = context['file'].upload_file.path
        ext = script_path.split('.')[-1]

        # run script on the page
        if request.POST.get("button_run_script"):
            t = open(vh.get_temp(), 'w')
            if ext == 'sh':
                subprocess.call(['sh', script_path] + arguments, stdout=t)
            elif ext == 'py':
                subprocess.run([sys.executable, script_path] + arguments, text=True, stdout=t)
            t.close()

            with open(vh.get_temp(), 'r') as t:
                for line in t:
                    output_text.append(line)
            t.close()

        # schedule the task with the selected date values
        if request.POST.get("button_task_schedule"):
            args = [context['file'], arguments]

            context['task_dates_original'] = []
            task_dates = []
            for t in context['task_scheduler']:
                context['task_dates_original'].append(request.POST.get(t))
                task_dates.append(request.POST.get(t))

            print(context['task_dates_original'])
            rt.validate_dates(task_dates, context)
            print("task dates", task_dates)
            valid = True

            for t in context['task_scheduler']:
                print(context[t], context[t][0])

            for t in context['task_scheduler']:
                if not context[t][0]:
                    print("breaking on ", t)
                    valid = False
                    break

            task_year, task_month, task_day, task_week, task_day_of_week, task_hour, task_minute, task_second \
                = task_dates

            # create tasks in scheduler and filetask in database
            if valid:
                # scheduler.add_job(rt.do_task, 'cron', args=args, id=context['file'].script_name,
                #                   year=task_year, month=task_month, day=task_day,
                #                   week=task_week, day_of_week=task_day_of_week,
                #                   hour=task_hour, minute=task_minute, second=task_second,
                #                   replace_existing=True)

                scheduler.add_job(rt.run_script, 'cron', args=args, id=context['file'].script_name,
                                  year=task_year, month=task_month, day=task_day,
                                  week=task_week, day_of_week=task_day_of_week,
                                  hour=task_hour, minute=task_minute, second=task_second,
                                  replace_existing=True)

                # save arguments
                task_args = vh.arg_parse().join(arguments)

                # create job details
                next_run, file_time, epoch_time = rt.get_next_run_time(context['file'].script_name)
                context['file'].filetask_set.update_or_create(
                    file_task_name=context['file'].script_name,
                    defaults={
                        'next_run': next_run, 'file_time': file_time, 'epoch_time': epoch_time,
                        'task_year': task_year, 'task_month': task_month, 'task_day': task_day,
                        'task_week': task_week, 'task_day_of_week': task_day_of_week,
                        'task_hour': task_hour, 'task_minute': task_minute, 'task_second': task_second,
                        'task_args': task_args
                    }
                )

                # make logs folder
                if not os.path.exists(vh.get_logs_dir()):
                    os.makedirs(vh.get_logs_dir())

        # remove task tied to this script
        if request.POST.get("button_remove_task"):

            if FileTask.objects.filter(file_task_name=context['file'].script_name).exists():
                context['file'].filetask_set.get(file_task_name=context['file'].script_name).delete()

            job = scheduler.get_job(job_id=context['file'].script_name)
            if job is not None:
                job.remove()

    if FileTask.objects.filter(file_task_name=context['file'].script_name).exists():
        file_task = context['file'].filetask_set.get(file_task_name=context['file'].script_name)
        context['last_run'] = file_task.last_run
        context['next_run'] = file_task.next_run

    context['fileContent'] = vh.get_file_content(context['file'].upload_file.path)
    context['output'] = output_text

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
    upload = UploadFileModel.objects.get(pk=file_id)
    context = {
        'url': url,
        'file': upload,
        'filename': url.split('/')[-1],
    }
    vh.get_perms(request, script_list, context)

    if request.method == 'POST':
        if request.POST.get("button_edit"):
            ext = '.' + context['filename'].split('.')[-1]
            request.session['new_file_name'] = request.POST.get("new_file_name")
            request.session['new_script_name'] = request.POST.get("new_script_name")
            vh.write_to_file(request.POST.get('script_edit'), vh.get_temp())
            context['fileContent'] = vh.get_file_content(vh.get_temp())

            context['new_file_name'] = request.POST.get("new_file_name").split('.')[0] + ext
            context['new_script_name'] = request.POST.get("new_script_name")

            return render(request, 'runscript/script_confirm_edit.html', context)

        if request.POST.get("button_edit_yes"):
            # NO LONGER IN USE
            # new script name
            # if request.session.get('new_script_name') != '':
            #     new_script_name = request.session.get('new_script_name')
            #     upload.script_name = new_script_name
            #     upload.save()
            #
            #     try:
            #         del request.session['newscriptname']
            #     except KeyError:
            #         pass

            if request.session.get('new_file_name') != '':
                new_file_name = request.session.get('new_file_name')
                # get original extension and filepath
                ext = url.split('.')[-1]

                # get new file name then add on original extension
                new_file_name = new_file_name.split('.')[0] + '.' + ext

                # split original file path, and replace the last element with new file name, joins them all
                new_file_path = url.split('/')
                new_file_path[-1] = new_file_name
                new_file_path = '/'.join(new_file_path)

                # remove first character from the string '/'
                # update the filepath with new file name
                url = new_file_path[1:]
                file_path = file_path.split('/')
                file_path[-1] = new_file_name
                file_path = '/'.join(file_path)

                upload.upload_file = url
                upload.save()

                job = scheduler.get_job(job_id=context['file'].script_name)
                if job is not None:
                    task = context['file'].filetask_set.get(file_task_name=context['file'].script_name)
                    task_args = task.task_args.split(vh.arg_parse())
                    args = [context['file'], task_args]
                    job.modify(args=args)

                try:
                    del request.session['new_file_name']
                except KeyError:
                    pass

            temp = open(vh.get_temp(), 'r')
            vh.write_to_file(temp, file_path)
            temp.close()
            script_log = f"{request.user} edited {context['file']}"
            current_time = datetime.datetime.now().strftime('%a %b %d, %Y %I:%M:%S %p')
            script_list.scriptlog_set.create(action=script_log, person=request.user, date_added=current_time)

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
            current_time = datetime.datetime.now().strftime('%a %b %d, %Y %I:%M:%S %p')
            script_list.scriptlog_set.create(action=script_log, person=request.user, date_added=current_time)

            job = scheduler.get_job(job_id=context['script_name'].script_name)
            if job is not None:
                job.remove()

            return redirect('runscript:view_and_upload', context['script_name'].script_list_id)

    return render(request, 'runscript/script_confirm_delete.html', context)


# changed page_obj to logs for pagination
@login_required(login_url='/login/')
@AccessCheck
def logs(request, list_id):
    script_list = ScriptList.objects.get(pk=list_id)

    context = {
        # 'logs': script_list.scriptlog_set.all()[::-1],
        'logs': script_list.tasklog_set.all()[::-1],
        'pk': list_id,
        'is_paginated': True,
    }

    # default
    if request.session.get('log_session') is None:
        context['search_log'] = "search_task"
        request.session['log_session'] = context['search_log']
        context['header'] = ["Script", "Date Ran", "Status"]

    vh.get_perms(request, script_list, context)

    if request.method == "POST":
        if request.POST.get("button_task_logs"):
            context['search_log'] = "search_task"
            request.session['log_session'] = context['search_log']
            request.session['log_search_session'] = ''
        if request.POST.get("button_user_logs"):
            context['search_log'] = "search_user"
            request.session['log_session'] = context['search_log']
            request.session['log_search_session'] = ''

    if request.method == "GET":
        if request.GET.get("button_search_log"):
            print("input text", request.GET.get("search_log_input"))
            request.session['log_search_session'] = request.GET.get("search_log_input")

    search = request.session.get("log_search_session")

    if request.session.get('log_session') == 'search_task':
        task_log = script_list.tasklog_set
        filter_log = task_log.filter(task_id__icontains=search) | \
            task_log.filter(time_ran__icontains=search)

        context['search_log'] = "search_task"
        context['header'] = ["Script", "Date Ran", "Output"]
        # context['logs'] = get_log_page(request, script_list.tasklog_set.all()[::-1])
        context['logs'] = get_log_page(request, filter_log[::-1]) or \
            get_log_page(request, script_list.tasklog_set.all()[::-1])
    elif request.session.get('log_session') == 'search_user':
        user_log = script_list.scriptlog_set
        filter_log = user_log.filter(action__icontains=search) | \
            user_log.filter(person__icontains=search) | \
            user_log.filter(date_added__icontains=search)

        context['search_log'] = "search_user"
        context['header'] = ["Date", "Person", "Action"]
        # context['logs'] = get_log_page(request, script_list.scriptlog_set.all()[::-1])
        context['logs'] = get_log_page(request, filter_log[::-1]) or \
            get_log_page(request, script_list.scriptlog_set.all()[::-1])

    context['search_input'] = request.session.get('log_search_session')
    print(request.session.get('log_search_session'))

    return render(request, 'runscript/logs.html', context)


def get_log_page(request, log):
    display_amt = 100
    paginator = Paginator(log, display_amt)
    page_num = request.GET.get("page")

    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    return page


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


@login_required(login_url='/login/')
@AccessCheck
def output(request, output_id):
    context = {
        'output': TaskLog.objects.get(pk=output_id),
        'id': output_id
    }

    return render(request, 'runscript/output.html', context)


def ajax_test(request):
    perm_attributes = vh.get_perm_attr()

    print(request.GET.get("forreal"))
    print(request.GET.get("nextnext"))

    if request.is_ajax():
        print("VERY COOL THIS IS AJAX")
        print("this user was selected:", request.GET.get("selected"))

    return JsonResponse({'notuser': perm_attributes})
