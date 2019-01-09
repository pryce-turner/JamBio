from django.db import models

class ExecutionStats(models.Model):
    wo_id = models.CharField(max_length=20)

    ANALYSIS_TYPE = (
        ('FQC', 'FastQC'),
        ('MQC', 'MultiQC'),
        ('QD',  'Enqueing')
    )
    analysis_type = models.CharField(
        max_length=10,
        choices=ANALYSIS_TYPE,
        default='',
    )
    exec_date = models.DateTimeField()
    EXEC_STATUS = (
        ('INIT', 'Initial State'),
        ('ENQD', 'Enqueued'),
        ('OK',   'OK'),
        ('FAIL', 'Fail')
    )
    exec_status = models.CharField(
        max_length=4,
        choices=EXEC_STATUS,
        default='INIT',
    )
    details = models.CharField(max_length=256, null=True)

    def __str__(self):
        return 'WO: ' + self.wo_id
