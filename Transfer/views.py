import datetime
import os
from django.shortcuts import render
from django.views import generic
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.forms import ModelForm
from django.db import transaction

from .models import ComponentInformation, TubeInformation, CoreData, ExecutionStats
from .constants import PROJECT_STORAGE
from .forms import ImportCompareForm
from .utils import error_logger, SubmissionExcelParser, FastQParser, DataComparison

def status_logger(project_id, status, details):
    """Creates database entries for failed / erroneous runs"""
    ExecutionStats.objects.create(
        project_id = project_id,
        exec_date = datetime.datetime.now(),
        exec_status = status,
        fail_reason = details
    )

def import_and_compare_handler(request):

    if request.method == 'POST':

        project_directory = ''
        fastq_directory = ''
        uploadedFilePath = None

        form = ImportCompareForm(request.POST,
                                 request.FILES)
        # check whether it's valid:
        if form.is_valid():
            fastq_directory = form.cleaned_data['fastq_directory_direct_path']

            if fastq_directory == None or len(fastq_directory) == 0:
                project_directory = form.cleaned_data['project_directory_pulldown']
                fastq_directory = os.path.join(project_directory, 'FastQ_Files')

            if not os.path.isdir(fastq_directory):
                return HttpResponse('Invalid Core Facility Data Path: ' + fastq_directory, content_type="text/plain")

            submissionSheetFile = form.cleaned_data['sub_sheet']
            delete_previous     = form.cleaned_data['delete_previous']
            uploadedFilePath    = handle_uploaded_file(submissionSheetFile, project_directory)

            try:
                comparison_output = import_and_compare(submissionSheetFile, fastq_directory, delete_previous)
            except Exception as fail:
                status_logger(fail.args[0], 'FAIL', (fail.args[1] + fail.args[2]))
                return HttpResponse('Run failed because of {}'.format(fail.args), content_type="text/plain")

            return HttpResponse(comparison_output, content_type="text/plain")
    else:
        form = ImportCompareForm()
        return render(request, 'Transfer/generic_form.html', {'form': form})


@transaction.atomic
def delete_preexisting_wo_objects(project_id):
    CoreData.objects.filter(project_id=project_id).delete()
    ComponentInformation.objects.filter(project_id=project_id).delete()
    TubeInformation.objects.filter(project_id=project_id).delete()


def import_and_compare(sub_sheet_path, fastq_directory, delete_previous):

        # Create customer submission sheet instance
        current_sheet = SubmissionExcelParser(sub_sheet_path)
        print('Excel parser initialized')

        preexisting_wo_objects = (
            CoreData.objects.filter(project_id=current_sheet.project_id_from_sheet).count() +
            ComponentInformation.objects.filter(project_id=current_sheet.project_id_from_sheet).count() +
            TubeInformation.objects.filter(project_id=current_sheet.project_id_from_sheet).count()
        )

        print('Checking for pre-existing WO objects')
        if preexisting_wo_objects > 0:
            if delete_previous == True:
                delete_preexisting_wo_objects(current_sheet.project_id_from_sheet)
            else:
                status_logger(current_sheet.project_id_from_sheet, 'FAIL', "Duplicate Work Order ID")
                message = (
                    "There are already %i database entries for Work Order: %s. "
                    "You can delete them by checking the box on the form."
                    % (preexisting_wo_objects, current_sheet.project_id_from_sheet)
                    )
                return message

        try:
            current_sheet.find_columns()
        except Exception as fail:
            print(fail)
            fail.args = (current_sheet.project_id_from_sheet, fail.args, 'Failed finding columns.')
            raise

        print('Found columns.')

        if current_sheet.submission_type == 'Individual Libraries':
            try:
                current_sheet.parse_individual_library_submission()
                print('Individual library columns extracted.')
            except Exception as fail:
                print(fail)
                fail.args = (current_sheet.project_id_from_sheet, fail.args, 'Failed parsing individual libraries.')
                raise


        elif current_sheet.submission_type == 'Pooled Libraries':
            try:
                current_sheet.parse_pool_submission()
                print('Pooled library columns extracted.')
            except Exception as fail:
                print(fail)
                fail.args = (current_sheet.project_id_from_sheet, fail.args, 'Failed parsing pooled libraries.')
                raise

        # Create fastQ parsing instance
        try:
            importer = FastQParser(fastq_directory, current_sheet.project_id_from_sheet)
        except Exception as fail:
            print(fail)
            fail.args = (current_sheet.project_id_from_sheet, fail.args, 'Failed to initialize FastQ parser')
            raise

        try:
            importer.parse_fastq_files() > 0
        except Exception as fail:
            print(fail)
            fail.args = (current_sheet.project_id_from_sheet, fail.args, 'No fastq files in directory: {}'.format(fastq_directory))
            raise

        # Create comparison instance
        try:
            comparer = DataComparison(current_sheet.project_id_from_sheet)
        except Exception as fail:
            print(fail)
            fail.args = (current_sheet.project_id_from_sheet, fail.args, 'Failed to initialize DataComparison object')
            raise

        try:
            comparer.compare_data()
            status_logger(current_sheet.project_id_from_sheet, 'OK', comparer.comparison_output)
        except Exception as fail:
            print(fail)
            fail.args = (current_sheet.project_id_from_sheet.encode, fail.args, "Failed on 'compare_data' method")
            raise

        return comparer.comparison_output


def handle_uploaded_file(file_, proj_dir):
    newPath = os.path.join(
        proj_dir, 'Sample_Sheet',
        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.xlsx'
    )

    with open(newPath, 'wb+') as destination:
        for chunk in file_.chunks():
            destination.write(chunk)
        destination.close()

    return newPath
