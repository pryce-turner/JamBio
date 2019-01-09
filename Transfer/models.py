from django.db import models
from .constants import PROJECT_STORAGE


class TubeInformation(models.Model):
    project_id = models.CharField(max_length=20)
    tube_id = models.CharField(max_length=40)
    pool_id = models.CharField(max_length=30, help_text="The name of the pooled library, may be a sample ID or tube ID", null=True)
    volume = models.CharField(max_length=40, null=True)
    concentration = models.CharField(max_length=40, null=True)
    total_amount = models.CharField(max_length=40, null=True)
    quantitation_method = models.CharField(max_length=40, null=True)
    buffer = models.CharField(max_length=40, null=True)
    organism = models.CharField(max_length=40, null=True)

    def __str__(self):
        return 'Tube ID: ' + self.tube_id

class ComponentInformation(models.Model):
    project_id = models.CharField(max_length=20)
    pool_id = models.CharField(max_length=30, help_text="The name of the pooled library, may be a sample ID or tube ID", null=True)
    sample_id = models.CharField(max_length=30, help_text="Individual component identifiers, may be index names or other customer provided name.")
    i7_index_name = models.CharField(max_length=30, null=True)
    i5_index_name = models.CharField(max_length=30, null=True)
    i7_index_sequence = models.CharField(max_length=40, null=True)
    i5_index_sequence = models.CharField(max_length=40, null=True)

    def __str__(self):
        return 'Sample ID: ' + self.sample_id

class CoreData(models.Model):
    project_id = models.CharField(max_length=20)
    pool_id = models.CharField(max_length=30, help_text="The name of the pooled library, may be a sample ID or tube ID", null = True)
    sample_id = models.CharField(max_length=30, help_text="Individual component identifiers, should map to customer provided name.")
    flowcell_id = models.CharField(max_length=40, help_text="Unique illumina flowcell the sample was run on.")
    lane = models.CharField(max_length=30)
    read = models.CharField(max_length=30)
    i7_index_sequence = models.CharField(max_length=40)
    i5_index_sequence = models.CharField(max_length=40, null = True)
    filename = models.CharField(max_length=100)

    def __str__(self):
        return 'Filename: ' + self.filename

class ExecutionStats(models.Model):
    project_id = models.CharField(max_length=20)
    exec_date = models.DateTimeField()
    EXEC_STATUS = (
        ('INIT', 'Initial State'),
        ('OK', 'OK'),
        ('FAIL', 'Fail')
    )
    exec_status = models.CharField(
        max_length=4,
        choices=EXEC_STATUS,
        default='INIT',
    )
    fail_reason = models.TextField()

    def __str__(self):
        return 'WO: ' + self.project_id
