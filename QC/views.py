import os
from time import gmtime, strftime
import glob

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.utils import timezone
from django.core.signing import Signer

import redis
import django_rq

from .constants import PROJECT_STORAGE
from .forms import ProjectDirInputForm
from .models import ExecutionStats
from .utils import QC, status_logger

## Instantiate redis queue, the following 2 commands must be run
## to init the message broker and worker.
# $> redis-server
# $> python3 manage.py rqworker default
q = django_rq.get_queue('default')
signer = Signer()

def run_qc_handler(request):
    """Run FastQC on all the FastQ files in a given directory.

    The form collects the fastq directory and associated work order ID.
    It will loop through all the fastq files and add them to the queue
    specified above.

    Exceptions with underlying 'runner' will be handled and logged by the
    runner - see QC.utils.FastQC for details.
    """

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ProjectDirInputForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            project_dir = form.cleaned_data['project_dir']
            project_id = project_dir.split('/')[-1]
            timestamp = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

            try:
                runner = QC(project_id, project_dir, timestamp)
            except Exception as error:
                return HttpResponse(error)

            try:
                fastqc_result = q.enqueue(runner.run_aggregated_qc)
            except redis.exceptions.ConnectionError as error:
                return HttpResponse(
                    "Redis could not connect to a queue, please ensure "
                    "that redis-server is installed and running."
                    )

            status_logger(
                project_id,
                'ENQD',
                'QD',
                f'Job ID: {fastqc_result.id}'
                )

            return HttpResponse(
                "Successfully added files for processing. "
                "Please come back later to view report. "
                f"Job ID: {fastqc_result.id}"
                )

        else:
            return HttpResponse("Form invalid.")

    # if a GET (or any other method), return a blank form
    else:
        form = ProjectDirInputForm()
        return render(request, 'QC/form_generic.html', {'form': form})

def list_projects(request):
    """Simple function for displaying all projects. """

    proj_dirs = []
    for proj_dir in os.listdir(PROJECT_STORAGE):
        proj_dirs.append([proj_dir, signer.sign(proj_dir)])
    return render(request, 'QC/all_projects.html', {'dirlist' : proj_dirs})

def show_report(request, proj_id_hash):
    """ Retrieve MultiQC report for a projectself.

    Takes a hashed project id, unsigns it and finds project directory.
    It will then find the most recent analysis performed and return the
    MultiQC report. If the analysis is still underway, it will return
    a (rough) percentage complete.
    """

    project_id = signer.unsign(proj_id_hash)
    project_dir = os.path.join(PROJECT_STORAGE, project_id)

    all_analyses = [dir for dir in os.listdir(project_dir) if dir.startswith('QC_Output')]

    if len(all_analyses) == 0:
        return HttpResponse('No analyses found for Project ' + str(project_id))
    elif len(all_analyses) == 1:
        most_recent_analysis = os.path.join(project_dir, all_analyses[0])
    else:
        sorted_analyses = all_analyses.sort()
        most_recent_analysis = os.path.join(project_dir, sorted_analyses[-1])

    total_fastq = 0
    total_fastqc = 0

    for root, dirs, files in os.walk(project_dir):
        for filename in files:
            if filename.endswith('fastq.gz'):
                total_fastq += 1

    for root, dirs, files in os.walk(most_recent_analysis):
        for filename in files:
            if filename.endswith('fastqc.html'):
                total_fastqc += 1
            if filename.endswith('multiqc_report.html'):
                report_path = os.path.join(root, filename)
                print(f"Report Path: {report_path}")
                return HttpResponse(QC.display_multiqc(report_path))
                break

    progress = total_fastqc / total_fastq

    return HttpResponse(
        "MultiQC report not yet ready. "
        f"FastQC is still processing with {progress*100} percent completion."
        )
