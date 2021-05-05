from django.contrib import admin
from .models import UploadFileModel, ScriptList, ScriptLog

# Register your models here.
admin.site.register(UploadFileModel)
admin.site.register(ScriptList)
admin.site.register(ScriptLog)
