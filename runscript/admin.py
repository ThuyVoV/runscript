from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import UploadFileModel, ScriptList, ScriptLog, TaskLog, FileTask

# Register your models here.
admin.site.register(UploadFileModel)
admin.site.register(ScriptList)
admin.site.register(ScriptLog)
admin.site.register(TaskLog)
admin.site.register(FileTask)
admin.site.register(Permission)
