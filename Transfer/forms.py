from django.forms import ModelForm, Form, FilePathField, CharField, ModelChoiceField, FileField, BooleanField
from django.forms.widgets import TextInput
from .constants import PROJECT_STORAGE
from .models import ComponentInformation, CoreData
import os

class ImportCompareForm(Form):
    sub_sheet            = FileField(label = "Completed Sample Sheet")
    project_directory    = FilePathField(
                               path=PROJECT_STORAGE,
                               allow_files=False,
                               allow_folders=True,
                               label='Project Directory',
                               required=False)
    outside_directory    = CharField(
                               widget=TextInput(attrs={'size': '80'}),
                               label="Path to current FastQ location.",
                               required=False)
    delete_previous      = BooleanField(
                               required=False,
                               label="Delete all objects for this project currently in the database?")
