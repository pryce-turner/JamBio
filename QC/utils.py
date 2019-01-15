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
from .forms import ProjectDirInputForm
from .models import ExecutionStats

def status_logger(project_id, status, analysis_type, details=None, exec_time=None):
    """Creates a timestamped log for every step of the analysis."""
    ExecutionStats.objects.create(
        project_id = project_id,
        exec_status = status,
        analysis_type = analysis_type,
        details = details,
        exec_date = exec_time if exec_time != None else timezone.now()
    )

class QC(object):
    """Run FastQC on all the FastQ files in a given directory.

    The form collects the fastq directory and associated work order ID.
    It will loop through all the fastq files and add them to the queue
    specified above.

    Exceptions with underlying 'runner' will be handled and logged by the
    runner - see QC.utils.FastQC for details.
    """

    def __init__(self, project_id, proj_dir, timestamp):
        """Defines paths and creates directories for analysis output."""

        self.project_id = project_id
        self.timestamp = timestamp
        self.project_dir = proj_dir

        self.run_output_dir = os.path.join(proj_dir, 'QC_Output_at_' + timestamp)

        self.fastqc_output_dir = os.path.join(self.run_output_dir, 'FastQC')
        self.multiqc_input_dir = self.fastqc_output_dir
        self.multiqc_output_dir = os.path.join(self.run_output_dir, 'MultiQC')

        os.mkdir(self.run_output_dir)
        os.mkdir(self.multiqc_output_dir)
        os.mkdir(self.fastqc_output_dir)

        print(f"Output Directory: {self.run_output_dir}")

    def run_aggregated_qc(self):
        """Aggregation function for calling analyses together. """
        if self.run_fastqc() == 0:
            return self.run_multiqc()

        return 1 # Failure

    def run_fastqc(self):
        """ Runs fastqc on all 'fastq.gz' files in given directory.

        FastQC has to be callable with 'fastqc' on your system for the
        subprocess call to work.
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
                        status_logger(self.project_id, 'FAIL', 'FQC', details=fastqc_proc.stderr)
                        return fastqc_proc.returncode

        print('FastQC successful.')
        status_logger(self.project_id, 'OK', 'FQC', details='FastQC successful.')

        return fastqc_proc.returncode

    def run_multiqc(self):
        """Runs MultiQC on the fastqc files generated during this analysis."""

        multiqc_command = [
            "multiqc",
            self.multiqc_input_dir,
            "-o",
            self.multiqc_output_dir,
            "-i",
            self.project_id
            ]

        multiqc_proc = subprocess.run(
            multiqc_command,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            encoding='utf-8'
            )

        if multiqc_proc.returncode == 0:
            status_logger(self.project_id, 'OK', 'MQC', details=multiqc_proc.stdout)
        else:
            status_logger(self.project_id, 'FAIL', 'MQC', details=multiqc_proc.stderr)

        return multiqc_proc.returncode

    @staticmethod
    def display_multiqc(path):
        """Opens and serves a MultiQC report."""

        myfile = open(path)
        data = myfile.read()
        return HttpResponse(data)
