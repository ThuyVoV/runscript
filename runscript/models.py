from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class ScriptList(models.Model):
    user = models.ManyToManyField(User, related_name="user_script_list")
    list_name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)

    def __str__(self):
        return self.list_name


class ScriptLog(models.Model):
    script_list = models.ForeignKey(ScriptList, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=100, default='')
    person = models.CharField(max_length=100, default='')
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.action


class UploadFileModel(models.Model):
    script_list = models.ForeignKey(ScriptList, on_delete=models.CASCADE, null=True)
    script_name = models.CharField(max_length=50, default='')
    date_added = models.DateTimeField(default=timezone.now)
    upload_file = models.FileField(upload_to='runscript/scripts')

    def __str__(self):
        return self.script_name
