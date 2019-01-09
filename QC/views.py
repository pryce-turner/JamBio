import os
from time import gmtime, strftime
import glob

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.utils import timezone
from django.core.signing import Signer

from redis import Redis
import django_rq

from .constants import PROJECT_STORAGE
from .forms import FastQDirInputForm
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
        form = FastQDirInputForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            fastq_dir = form.cleaned_data['fastq_dir']
            wo_id = form.cleaned_data['wo_id']
            timestamp = strftime("%Y-%m-%d-%H-%M-%S", gmtime())

            try:
                runner = QC(wo_id, fastq_dir, timestamp)
            except Exception as error:
                return HttpResponse(error)

            fastqc_result = q.enqueue(runner.run_aggregated_qc)

            status_logger(
                wo_id,
                'ENQD',
                'QD',
                'Job ID: ' + fastqc_result.id
            )

            return HttpResponse((
                "Successfully added files for processing. "
                "Please come back later to view report. "
                "Job ID: {}").format(fastqc_result.id)
                )

        else:
            return HttpResponse("Form invalid.")

    # if a GET (or any other method), return a blank form
    else:
        form = FastQDirInputForm()
        return render(request, 'QC/form_generic.html', {'form': form})

def list_projects(request):

    wo_dirs = []
    for wo_dir in os.listdir(PROJECT_STORAGE):
        wo_dirs.append([wo_dir, signer.sign(wo_dir)])
    return render(request, 'QC/workorders.html', {'dirlist' : wo_dirs})

def show_report(request, order_id_hash):

    order_id = signer.unsign(order_id_hash)

    if str(order_id).lower().startswith('wo-'):
        wo_id = str(order_id)
    else:
        wo_id = str(ExecutionStats.objects.filter(website_order_id = order_id).latest('exec_date').wo_id)

    project_dir = os.path.join(PROJECT_STORAGE, wo_id)
    out_dirs = []

    for out_dir in os.listdir(project_dir):
        if out_dir.startswith('QC_Output'):
            out_dirs.append(out_dir)

    out_dirs.sort()

    output_dir = os.path.join(project_dir, out_dirs[-1])

    if not os.path.isdir(output_dir):
        return HttpResponse('No result found for Work-Order ' + str(wo_id))

    total_fastq = 0
    total_fastqc = 0

    for root, dirs, files in os.walk(project_dir):
        for filename in files:
            if filename.endswith('fastq.gz'):
                total_fastq += 1

    for root, dirs, files in os.walk(output_dir):
        for filename in files:
            if filename.endswith('fastqc.html'):
                total_fastqc += 1
            if filename.endswith('multiqc_report.html'):
                report_path = os.path.join(root, filename)
                print('report_path: ' + report_path)
                return HttpResponse(QC.display_multiqc(report_path))
                break

    progress = total_fastqc / total_fastq

    return HttpResponse(('MultiQC report not yet ready. FastQC is still processing with {} percent completion.').format(progress*100))
