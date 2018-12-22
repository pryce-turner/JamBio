import os
import shutil
from time import gmtime, strftime

from django.test import TestCase, Client
from django.urls import reverse, path
from django.utils import timezone

from .views import QC
from .models import ExecutionStats
from .constants import PROJECT_STORAGE
from .forms import FastQDirInputForm

class QCTest(TestCase):

    def setUp(self):

        self.proj_id = 'WO-000000QC'
        self.timestamp = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
        self.project_directory = os.path.join(PROJECT_STORAGE, self.proj_id)

        self.runner = QC(self.proj_id, self.project_directory, self.timestamp)
        self.assertTrue(os.path.isdir(self.runner.run_output_dir))

    def test_input_form(self):
        form_data = {
        'wo_id' : self.proj_id,
        'fastq_dir' : os.path.join(PROJECT_STORAGE, self.proj_id)
        }
        form = FastQDirInputForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_qc_run(self):

        # Test FastQC

        self.runner.run_fastqc()

        self.assertTrue(os.path.isdir(self.runner.fastqc_output_dir))

        expected_stat = 'OK'
        actual_stat = ExecutionStats.objects.get(wo_id=self.proj_id).exec_status

        expected_reports = 2
        actual_reports = 0
        for out_file in os.listdir(path=self.runner.fastqc_output_dir):
            if '.html' in out_file: actual_reports += 1

        self.assertEqual(expected_stat, actual_stat)
        self.assertEqual(expected_reports, actual_reports)

        # Test MultiQC

        self.runner.run_multiqc()

        self.assertTrue(os.path.isdir(self.runner.multiqc_output_dir))

        expected_report_path = os.path.join(
            self.runner.multiqc_output_dir, self.proj_id +
            '_multiqc_report.html'
            )
        self.assertTrue(os.path.isfile(expected_report_path))

        # Test report fetching

        id_hash = 'WO-000000QC:GKUfwYU0-724mSN71sMvWmtdor0/'
        c= Client()
        response = c.get('/QC/reports/' + id_hash)
        self.assertEqual(response.status_code, 200)


    def tearDown(self):
        if os.path.exists(self.runner.run_output_dir):
            shutil.rmtree(self.runner.run_output_dir)
