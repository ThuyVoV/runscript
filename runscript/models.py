from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class ScriptList(models.Model):
    user = models.ManyToManyField(User, related_name="user_script_list")
    list_name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)

    class Meta:
        ordering = ['list_name']

    def __str__(self):
        return f"{self.owner} - {self.list_name}"


class ScriptLog(models.Model):
    script_list = models.ForeignKey(ScriptList, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=100, default='')
    person = models.CharField(max_length=100, default='')
    #date_added = models.DateTimeField(default=timezone.now)
    date_added = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.action


class TaskLog(models.Model):
    script_list = models.ForeignKey(ScriptList, on_delete=models.CASCADE, null=True)

    task_id = models.CharField(max_length=100, default='')
    time_ran = models.CharField(max_length=100, default='')

    task_output = models.TextField()

    def __str__(self):
        return self.task_id + ' - ' + self.time_ran


class UploadFileModel(models.Model):
    script_list = models.ForeignKey(ScriptList, on_delete=models.CASCADE, null=True)
    script_name = models.CharField(max_length=50, default='', unique=True)
    date_added = models.DateTimeField(default=timezone.now)
    upload_file = models.FileField(upload_to='runscript/scripts')

    class Meta:
        ordering = ['script_name']

    def __str__(self):
        return self.script_name


class FileTask(models.Model):
    upload_file_model = models.ForeignKey(UploadFileModel, on_delete=models.CASCADE, null=True)

    file_task_name = models.CharField(max_length=100, default='')
    last_run = models.CharField(max_length=100, default='')
    next_run = models.CharField(max_length=100, default='')

    task_year = models.CharField(max_length=100, default='')
    task_month = models.CharField(max_length=100, default='')
    task_week = models.CharField(max_length=100, default='')
    task_day = models.CharField(max_length=100, default='')
    task_day_of_week = models.CharField(max_length=100, default='')
    task_hour = models.CharField(max_length=100, default='')
    task_minute = models.CharField(max_length=100, default='')
    task_second = models.CharField(max_length=100, default='')

    task_args = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.file_task_name + " schedule"
