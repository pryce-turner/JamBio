from django.forms import ModelForm, Form, FilePathField, CharField, ModelChoiceField, FileField, BooleanField
from django.forms.widgets import TextInput
from .constants import PROJECT_STORAGE
from .models import ComponentInformation, CoreData
import os

class ImportCompareForm(Form):
    sub_sheet                   = FileField(label = 'Customer Submission Sheet')
    project_directory_pulldown  = FilePathField(path=PROJECT_STORAGE, allow_files=False, allow_folders=True, label='Core Data Folder')
    fastq_directory_direct_path = CharField(widget=TextInput(attrs={'size': '80'}), label='Or directly enter path here', required=False)
    delete_previous             = BooleanField(required=False, label = 'Delete all objects for this WO currently in the database?')
