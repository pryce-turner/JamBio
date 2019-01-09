import os
import subprocess
import shutil
from time import gmtime, strftime
import django_rq

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.utils import timezone

from .constants import PROJECT_STORAGE
from .forms import FastQDirInputForm
from .models import ExecutionStats

def status_logger(wo_id, status, analysis_type, details=None, exec_time=None):
    ExecutionStats.objects.create(
        wo_id = wo_id,
        analysis_type = analysis_type,
        exec_date = exec_time if exec_time != None else timezone.now(),
        exec_status = status,
        details = details
    )

class QC(object):
    """Run FastQC on all the FastQ files in a given directory.

    The form collects the fastq directory and associated work order ID.
    It will loop through all the fastq files and add them to the queue
    specified above.

    Exceptions with underlying 'runner' will be handled and logged by the
    runner - see QC.utils.FastQC for details.
    """

    def __init__(self, wo_id, proj_dir, timestamp):
        """Defines paths and creates directories for analysis output."""

        self.wo_id = wo_id
        self.timestamp = timestamp
        self.project_dir = proj_dir

        self.run_output_dir = os.path.join(proj_dir, 'QC_Output_at_' + timestamp)

        self.fastqc_output_dir = os.path.join(self.run_output_dir, 'FastQC')
        self.multiqc_input_dir = self.fastqc_output_dir
        self.multiqc_output_dir = os.path.join(self.run_output_dir, 'MultiQC')

        os.mkdir(self.run_output_dir)
        os.mkdir(self.multiqc_output_dir)
        os.mkdir(self.fastqc_output_dir)

        print('Output directory: ' + self.run_output_dir)

    def run_aggregated_qc(self):
        if self.run_fastqc() == 0:
            return self.run_multiqc()

        return 1 # Failure

    def run_fastqc(self):
        """ Runs FastQC from program location specified in 'constants'
        Make sure the path is correctly set and you've granted it exec
        permissions
        """

        for root, dirs, files in os.walk(self.project_dir):
            for filename in files:
                if filename.endswith('fastq.gz'):
                    fastq_path = os.path.join(root, filename)

                    fastqc_command = [
                        "fastqc",
                        fastq_path,
                        "-o",
                        self.fastqc_output_dir
                        ]

                    try:
                        fastqc_proc = subprocess.run(
                            fastqc_command,
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            encoding='utf-8'
                            )
                    except FileNotFoundError:
                        print(
                            "No FastQC executable on your system path."
                            "Please check FastQC is downloaded and "
                            "callable with 'fastqc'."
                            )
                        raise

                    if fastqc_proc.returncode != 0:
                        print(fastqc_proc.std_err)
                        status_logger(self.wo_id, 'FAIL', 'FQC', details=fastqc_proc.stderr)
                        return fastqc_proc.returncode

        print('FastQC successful.')
        status_logger(self.wo_id, 'OK', 'FQC', details='FastQC successful.')

        return fastqc_proc.returncode

    def run_multiqc(self):

        multiqc_command = [
            "multiqc",
            self.multiqc_input_dir,
            " -o ",
            self.multiqc_output_dir,
            " -i ",
            self.wo_id
            ]

        multiqc_proc = subprocess.run(
            multiqc_command,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            encoding='utf-8'
            )

        if multiqc_proc.returncode == 0:
            status_logger(self.wo_id, 'OK', 'MQC', details=multiqc_proc.stdout)
        else:
            status_logger(self.wo_id, 'FAIL', 'MQC', details=multiqc_proc.stderr)

        return multiqc_proc.returncode

    @staticmethod
    def display_multiqc(path):
        myfile = open(path)
        data = myfile.read()
        return HttpResponse(data)
