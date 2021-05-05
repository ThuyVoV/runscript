from django import forms
from .models import UploadFileModel, ScriptList


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFileModel
        fields = [
            "script_name",
            "upload_file"
        ]


class CreateScriptListForm(forms.ModelForm):
    class Meta:
        model = ScriptList
        fields = [
            "list_name"
        ]

# class CreateScriptListForm(forms.Form):
#     list_name = forms.CharField(max_length=100)
