from django import forms
from .constants import PROJECT_STORAGE
import os

class ProjectDirInputForm(forms.Form):
    project_dir = forms.FilePathField(
        path=PROJECT_STORAGE,
        allow_files=False,
        allow_folders=True,
        label="Project Directory"
        )
