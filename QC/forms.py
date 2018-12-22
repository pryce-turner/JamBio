from django import forms
from .constants import PROJECT_STORAGE
import os

class FastQDirInputForm(forms.Form):
    wo_id = forms.CharField(max_length=11, min_length=11)
    fastq_dir = forms.FilePathField(
        path=PROJECT_STORAGE,
        allow_files=False,
        allow_folders=True
        )
